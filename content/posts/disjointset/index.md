---
title: "Disjoint-Set"
date: 2024-03-24T14:42:34+08:00
draft: false
---

Data structure for maintaining relations between elements.
<!--more-->

# Definition:
The disjoint-set data structure is a data structure that is used to determine the set to which an element belongs. 

# Problem:
Take the following example:

A is with B, C is with D, E is with F, F is with C, G is with B.

1. What's the minimum number of sets to fit all the elements?
2. Are A and D in the same set?

# Solution:
Of course, we can use multiple linked lists to solve this. Disjoint-set is somewhat similar. Traditionally, disjoint-set is implemented as such:
```
int f[N];
void init() {
    for (int i = 1; i <= n; i++) f[i] = i;
}
```
Where `f[i]` is the parent of `i`. If `f[i] == i`, then `i` is the root of the set. If `f[i] != i`, then `i` is not the root of the set, and `f[i]` is the parent of `i`. To find the root, we implement a find() function, like so:
```
int find(int x) {
    return x == f[x] ? x : find(f[x]);
}
```
You may be wondering why do we need to to find the root of the set. The reason is that we can determine whether two elements are in the same set by comparing their roots. In other words, if `find(x) == find(y)`, then `x` and `y` are in the same set, as they have the same root.
To put two elements into the same set, we can do as such:
```
void merge(int x, int y) {
    f[find(x)] = find(y);
}
```
This function merges the set of `x` and the set of `y` by setting the root of `x` to the root of `y`.
For the example, we can solve it quite easily with disjoint-set:
```
init();
f[1] = 2;
f[3] = 4;
f[5] = 6;
f[6] = 3;
f[7] = 2;
```
Then we can answer the questions:
```
// 1. What's the minimum number of sets to fit all the elements?
int cnt = 0;
for (int i = 1; i <= n; i++) {
    if (f[i] == i) cnt++;
}
cout << cnt << endl;
// 2. Are A and D in the same set?
cout << (find(1) == find(4)) << endl;
```

But, as you probably noticed, the find() function gets quite inefficient when the tree is deep. To solve this, we can use the union by rank and path compression optimization. The union by rank optimization is quite simple. We just need to maintain the rank of each element, and merge the set with the smaller rank to the set with the larger rank. The path compression optimization is also quite simple. When we find the root of an element, we can set the parent of all the elements on the path to the root. The implementation is as follows:
```
int find(int x) {
    return x == f[x] ? x : f[x] = find(f[x]);
}
```
This way, each time an element is added to a set, the set is flattened, and the tree is kept shallow. But is this all?
Of course not.

# Optimization:
We add an additional information to the disjoint-set: the size of the set. This way, we can merge the smaller set to the larger set. Why is this necessary? Let's take a look at the following example:
```
1->2
 ->3
4->5->6
 ->7
```
If we merge 4 to 1, the tree will become:
```
1->2
 ->3
 ->4->5->6
    ->7
```
But if we merge 1 to 4, the tree will become:
```
4->5->6
 ->7
 ->1->2
    ->3
```
The first tree has the maximum depth of 4, while the second tree has the maximum depth of 3. This is why we need to merge the smaller set to the larger set - so that at its worst, the find() function wouldn't need to traverse as far.
To tackle this, we alter the `f[]` array to store the size of the set as well as the root information. The idea is like such:
1. If i is the root of the set, then `f[i]` is the negative value of the size of the set.
2. If i is not the root of the set, then `f[i]` is the parent of i.
3. When we merge, we merge the root of the smaller set to the root of the larger set, and update the size of the set.
Notice we used negativity to distinguish the root from the non-root. The implementation is as follows:
```
int f[N];
void init() {
    for (int i = 1; i <= n; i++) f[i] = -1;
}
int find(int x) {
    int t = x;
    while(f[t] > 0){
        t = f[t];
    }
    while(x != t){
        int tmp = f[x];
        f[x] = t;
        x = tmp;
    }
    return t;
}
void merge(int x, int y) {
    x = find(x);
    y = find(y);
    if(x == y) return;
    if (f[x] < f[y]) {
        f[x] += f[y];
        f[y] = x;
    } else {
        f[y] += f[x];
        f[x] = y;
    }
}
```
Notice that instead of recursively calling the find() function, we use a while loop to find the root of the set. This is because recursion can be quite inefficient, as each layer of recursion adds to the stack.
