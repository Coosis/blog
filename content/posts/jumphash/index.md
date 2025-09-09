+++
date = '2025-09-09T16:46:08+08:00'
draft = false
title = 'DB Sharding with Jump Hashing'
tags = ['database', 'sharding', 'jump hashing', 'hashing']
+++

So you want to shard your db but it's not power of two?
<!--more-->

# DB Sharding
From AWS:
> Database sharding is the process of storing a large database across 
> multiple machines. A single machine, or database server, can store and 
> process only a limited amount of data. Database sharding overcomes this 
> limitation by splitting data into smaller chunks, called shards, and storing 
> them across several database servers. All database servers usually have the 
> same underlying technologies, and they work together to store and process 
> large volumes of data.

# Routing using last bits of hash
One common way to shard is looking at a key's hash and taking 
the last few bits to determine which shard it belongs to. For 
example, if a hash is `0b10101100` and we have 8 shards, we look at 
the lower 3 bits `100` and determine that it belongs to shard 4.

This works great if the number of shards is a power of two. But what if 
it's not? Or, we want to add or remove shards?

# Modulo: Genius solution?
You might think it's a simple problem. We can use modulo operation! 
Because looking at lower bits is a kind of modulo operation. We can generalize it 
to arbitrary number of shards. Problem solved! ... right?

Well, to some degree. But there's a problem. When we add or remove a shard, 
lots of keys will be remapped to different shards. You can imagine this takes a heavy toll 
on performance. 

For example, if we have 3 shards called `S1`, `S2`, `S3`, and we have key hashes: 
`0 1 2 3 4 5 6 7 8`. They will be mapped to shards like this:
```
0 -> S1
1 -> S2
2 -> S3
3 -> S1
4 -> S2
5 -> S3
6 -> S1
7 -> S2
8 -> S3
```

Now if we add a shard `S4`, the mapping becomes:
```
0 -> S1
1 -> S2
2 -> S3
3 -> S4
4 -> S1
5 -> S2
6 -> S3
7 -> S4
8 -> S1
```

Notice how key hashes `3, 4, 5, 6, 7, 8` are ALL remapped to different shards.
This is bad.

# Jump Hashing
Introducing: Jump Hashing. What if I tell you, using this technique, 
when you add or remove a shard, only about `1/n` keys are remapped, where `n` is the number of shards?
Does such a wonderful technique exist? Yes it does! It's called Jump Hashing.

Here's how it works:
1. Say we have `N` shards already. 
2. We have a key `K`. 
3. There are two tasks: 
    1. We need to figure out which shard `K` belongs to, given `N`.
    2. Figure out how to operate when we add or remove a shard.

## Which Shard Does K Belong To?
We generate a sequence of random numbers between `0` and `1` denoted as `r(i)`, 
where `i` is the index of the random number, `1 <= i <= N-1` using `K` as the seed. 
`K` starts at shard `0`. For each shard `i` from `1` to `N-1`, we 
jump to shard `i` if `r(i)` is less than `1/(i+1)`.
Notice we are not jumping 1 shard each time, we are jumping to shard `i` directly, 
this could mean jumping from shard `3` to shard `7` directly.

From this, it's trivial to see that `K` ending at some shard `j` if and only if:
```
r(j) passed 1/(j+1) check
AND
for all i in [j+1, N-1], r(i) missed 1/(i+1) check
```
If we find such `j`, then `K` belongs to shard `j`.

## Adding Or Removing A Shard
When we add a shard, we just increase `N` by 1. 
When we remove a shard `j`, we just decrease `N` by 1.
So simple! But how does this make keys remap less?
Because the sequence derived from `K` is deterministic. 
When we add a shard, we only append a random number to the sequence for a 
specific key. If the appended random number does not pass the check(which has a 
somewhat high probability), then the key will not be remapped. 
When we remove a shard, only keys that were mapped to the removed shard will be remapped.

Now we have an intuitive understanding of how Jump Hashing works. Now let's do some math. 

# Distribution of Keys Is Uniform
In sharding we almost always want the distribution of keys to be uniform. That's 
because if one shard has way more keys than others, it will likely become a bottleneck, 
and losing that shard will have a significant impact. We want our shards distributing that 
risk. 

Let's prove that Jump Hashing distributes keys uniformly.
Concretely, we want to prove that for any key `K`, the probability of it 
ends up in shard `j` is `1/N`, where `N` is the number of shards, and `0 <= j <= N-1`.

From our earlier analysis, we know that `K` ends up in shard `j` if and only if 
it doesn't jump to any shard `i` where `j < i <= N-1`. The probability of not jumping 
to shard `i` is `1 - 1/(i+1) = i/(i+1)`. Since the random numbers are independent(we sure hope so), 
the probability of not jumping to any shard `i` where `j < i <= N-1` is:
$$
P(K\ ends\ up\ in\ shard\ j) = \frac{1}{j+1} \prod_{i=j+1}^{N-1} \frac{i}{i+1}
= \frac{1}{j+1} * \frac{j+1}{N} = \frac{1}{N}
$$

# Naive Implementation
But how do we actually implement this? We could of course mimic the algorithm directly. The 
first step is to generate the sequence of random numbers. Instead of only using `K` as the seed, 
we also mix in `i` so the sequence is derived from tuples `(K, 1)`, `(K, 2)`, ..., `(K, N-1)`. 
After that, we just iterate through the sequence and apply the algorithm directly: 
```pseudocode
b = 0
for i in 1..<N:
    r = random(K, i) # random number between 0 and 1 derived from (K, i)
    if r < 1/(i+1):
        b = i
return b
```

This is great. Except it isn't. The time complexity is `O(N)`. Can we do better?

# Efficient Implementation
Of course we can! At least, according to John Lamping and Eric Veach from Google. Their paper is listed at 
the end. 
If we look at the algorithm, we can see the position is governed by a list of jump indices. Let's look at the 
distribution of the jump indices. 
Suppose we are at position `b`. Let `j` be the next jump index. 
The probability of not jumping at `b+1, b+2, ..., t` is:
$$
P(not\ jumping\ at\ b+1,\ ...,\ t) = \prod_{i=b+1}^{t} (1-\frac{1}{i+1}) = \frac{b+1}{t+1}
$$
From this we get:
$$
P(j \leq t) = P(jumped\ at\ or\ before\ t) 
$$
$$
            = 1 - P(not\ jumping\ at\ b+1,\ ...,\ t) 
$$
$$
            = 1 - \frac{b+1}{t+1},\  t \geq b+1
$$

## Sampling
Okay now we have the distribution of the next jump index. How do we sample from it? 
If you are familiar with inverse transform sampling, this is easier to understand. 
1. Generate a random number `u` between `0` and `1` under uniform distribution. 
2. Find the smallest `j` such that 
$$
1 - \frac{b+1}{j+1} \geq u
$$
3. This simplifies to
$$
j = \lfloor \frac{b+1}{1-u} \rfloor
$$
4. Since `u` is uniformly distributed between `0` and `1`, `1-u` is also uniformly distributed between `0` and `1`. 
Substituting `1-u` with `u`, we get
$$
j = \lfloor \frac{b+1}{u} \rfloor
$$
5. If this math is too much, you can think of it this way: 
    1. Imaging a line of length `1`. We split it into parts, each part having length `p_i`. 
    2. We pick a random point on the line uniformly. 
    3. The probability of the point falling into part `i` is `p_i`.
    4. The probability of us jumping to index `j` is `P(j <= t) - P(j <= t-1)`, which 
    corresponds to the length of a part on the line.
    5. Using the aforementioned inequality, we can actually find the value of `j` directly. 

## Putting It All Together
So given current position `b`, we can sample and get the next jump index `j` directly. 
We can do this in a loop until `j` is out of range, like so: 
```pseudocode
b = 0
while true:
    u = uniform()
    j = floor((b+1)/u)
    if j >= N:
        return b
    b = j
```

## Implementation From Paper
```cpp
int32_t JumpConsistentHash(uint64_t key, int32_t num_buckets) {
    int64_t b = -1, j = 0;
    while(j < num_buckets) {
        b = j;
        key = key * 2862933555777941757ULL + 1;
        j = (b + 1) * (double(1LL << 31) / double((key>>33)+1));
    }
    return b;
}
```
You might be thinking, what the heck is that key manipulation? 
That's just a fast way to generate pseudo random numbers from a seed. Look up `LCG` for more details. 
The next `j` line obviously is a clever way to generate a denominator between `0` and `1`. 

This achieves `O(1)` time complexity. For concrete mathematical proof, see the paper. 


# Other Resources
1. [A Fast, Minimal Memory, Consistent Hash Algorithm, John Lamping, Eric Veach](https://arxiv.org/pdf/1406.2294)
