+++
date = '2026-05-24T21:03:43+08:00'
draft = false
title = "MySQL's LIMIT Caveat"
+++

Today, I came across a post with title "Adding LIMIT 1 Is 50 Times Slower". 
<!--more-->

# Scenario
The gist was this: given a table like this:
```sql
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uid INT,
    ctime TIMESTAMP,
    INDEX idx_uid (uid),
    INDEX idx_ctime (ctime)
);
```
And the query:
```sql
SELECT id, uid FROM orders WHERE uid = 1 ORDER BY ctime DESC LIMIT 1;
```
This query was slow, taking about 2.5 seconds to execute. Removing the `LIMIT 1` made it much faster. 
And the author explained the optimizer's thought process: "You want the newest row, desc by time, so using index on 
`ctime` and go back until the first row with `uid = 1` is probably the optimal plan". With this, the query 
eventually scanned almost 2 million rows, which is why it was so slow.

# Okay, So I Learned Something New?
If only it were that simple.
When I read the comments, I found people saying the explanation was wrong and offering different explanations.
Let's look at a few of those comments:
1. "You are blaming `LIMIT` when the fault is index on `ORDER BY` column".
2. "How is this related to `LIMIT`? The real problem is `ORDER BY` doesn't have index".
3. "I worked at Amazon and we had a similar issue. The problem was exactly `LIMIT`, removing it and only take first row in java solved the problem".
4. "This is caused by `ORDER BY` and not having index on the time column".

At this point, I was confused. What's the real story here? Let's find out.

# Data Generation
I spun up a MySQL instance and generated 1 million rows: 400k rows with `uid = 1` and an old `ctime`, and 600k rows with `uid > 1` and a newer `ctime`.

let’s actually start without an index on ctime to observe how the execution plan changes.
```sql
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uid INT,
    ctime TIMESTAMP,
    INDEX idx_uid (uid)
);
```

Rust code for generating data:
```rust
use chrono::Duration;
use sqlx::mysql::MySqlPool;

#[tokio::main]
async fn main() {
    println!("Hello, world!");
    let pool = MySqlPool::connect("mysql://root:passwd@localhost:3306/mysql").await.unwrap();
    let old_time = chrono::Utc::now() - Duration::days(30);
    for _ in 0..400_000 {
        sqlx::query("INSERT INTO orders (uid, ctime) VALUES (1, ?)")
            .bind(old_time)
            .execute(&pool)
            .await
            .unwrap();
    }
    let new_time = chrono::Utc::now();
    let total_others = 600_000;
    let concurrency = 10;
    let chunk = total_others / concurrency;

    let mut handles = vec![];
    for thread_id in 0..concurrency {
        let pool = pool.clone();
        let start = thread_id * chunk;
        let end = if thread_id == concurrency - 1 {
            total_others
        } else {
            start + chunk
        };
        handles.push(tokio::spawn(async move {
            for i in start..end {
                let uid = (i % 10000) + 2;  // uid 范围 2..10001
                sqlx::query("INSERT INTO orders (uid, ctime) VALUES (?, ?)")
                    .bind(uid)
                    .bind(new_time)
                    .execute(&pool)
                    .await
                    .unwrap();
            }
        }));
    }

    for handle in handles {
        handle.await.unwrap();
    }
}
```
Cargo.toml:
```toml
[package]
name = "mysql-test"
version = "0.1.0"
edition = "2024"

[dependencies]
chrono = "0.4.44"
sqlx = { version = "0.8", features = ["mysql", "runtime-tokio", "chrono"] }
tokio = { version = "1.52.3", features = ["full"] }
```

Now let's verify the data is in place as expected:
```text
mysql> select count(*) from orders;
+----------+
| count(*) |
+----------+
|  1000000 |
+----------+
1 row in set (0.052 sec)

mysql> select count(*) from orders where uid = 1;
+----------+
| count(*) |
+----------+
|   400000 |
+----------+
1 row in set (0.027 sec)
```
Perfect. Now we can begin. 

# Looking at Execution Plan
Let's look at the execution plan for the query with `LIMIT 1` and without `LIMIT 1`:
```text
mysql> EXPLAIN SELECT id, uid FROM orders WHERE uid = 1 ORDER BY ctime DESC LIMIT 1;
+--------------------------------------------------------------------------------------------+
| EXPLAIN                                                                                    |
+--------------------------------------------------------------------------------------------+
| -> Limit: 1 row(s)  (cost=51693 rows=1)
    -> Sort: orders.ctime DESC, limit input to 1 row(s) per chunk  (cost=51693 rows=499861)
        -> Index lookup on orders using idx_uid (uid = 1)  (cost=51693 rows=499861)
|
+--------------------------------------------------------------------------------------------+
1 row in set (0.001 sec)

mysql> EXPLAIN SELECT id, uid FROM orders WHERE uid = 1 ORDER BY ctime DESC;
+--------------------------------------------------------------------------------------------+
| EXPLAIN                                                                                    |
+--------------------------------------------------------------------------------------------+
| -> Sort: orders.ctime DESC  (cost=51693 rows=499861)
    -> Index lookup on orders using idx_uid (uid = 1)  (cost=51693 rows=499861)
|
+--------------------------------------------------------------------------------------------+
1 row in set (0.001 sec)
```
Both queries use the same index: `idx_uid`.

Now let's add the index on `ctime` and see how the execution plan changes:
```text
mysql> CREATE INDEX idx_ctime ON orders(ctime);
Query OK, 0 rows affected (0.506 sec)
Records: 0  Duplicates: 0  Warnings: 0

mysql> EXPLAIN SELECT id, uid FROM orders WHERE uid = 1 ORDER BY ctime DESC LIMIT 1;
+--------------------------------------------------------------------------------------------+
| EXPLAIN                                                                                                                                                                            |
+--------------------------------------------------------------------------------------------+
| -> Limit: 1 row(s)  (cost=0.00342 rows=1)
    -> Filter: (orders.uid = 1)  (cost=0.00342 rows=1)
        -> Index scan on orders using idx_ctime (reverse)  (cost=0.00342 rows=2)
|
+--------------------------------------------------------------------------------------------+
1 row in set (0.001 sec)

mysql> EXPLAIN SELECT id, uid FROM orders WHERE uid = 1 ORDER BY ctime DESC;
+--------------------------------------------------------------------------------------------+
| EXPLAIN                                                                                    |
+--------------------------------------------------------------------------------------------+
| -> Sort: orders.ctime DESC  (cost=51693 rows=499861)
    -> Index lookup on orders using idx_uid (uid = 1)  (cost=51693 rows=499861)
 |
+--------------------------------------------------------------------------------------------+
1 row in set (0.001 sec)
```
Huh, would you look at that. The query with `LIMIT 1` is now using the index on `ctime` and doing a reverse scan! This
is exactly what the original post said. 

# Actual Execution Time
Let's run the query with and without `LIMIT` and see how long it takes:
```text
mysql> SELECT id, uid FROM orders WHERE uid = 1 ORDER BY ctime DESC;
+--------+------+
| id     | uid  |
+--------+------+
| ...    |    1 |
| 217568 |    1 |
| 217569 |    1 |
+--------+------+
400000 rows in set (0.191 sec)

mysql> SELECT id, uid FROM orders WHERE uid = 1 ORDER BY ctime DESC LIMIT 1;
+--------+------+
| id     | uid  |
+--------+------+
| 400000 |    1 |
+--------+------+
1 row in set (0.268 sec)
```
The query with `LIMIT` 1 is actually slower than the query without `LIMIT`!

Let's remove the index on `ctime` and see how it changes:
```text
mysql> DROP INDEX idx_ctime ON orders;
Query OK, 0 rows affected (0.008 sec)
Records: 0  Duplicates: 0  Warnings: 0

mysql> SELECT id, uid FROM orders WHERE uid = 1 ORDER BY ctime DESC LIMIT 1;
+----+------+
| id | uid  |
+----+------+
|  1 |    1 |
+----+------+
1 row in set (0.164 sec)

mysql> SELECT id, uid FROM orders WHERE uid = 1 ORDER BY ctime DESC;
+--------+------+
| id     | uid  |
+--------+------+
| ...    |    1 |
| 217567 |    1 |
| 217568 |    1 |
| 217569 |    1 |
+--------+------+
400000 rows in set (0.172 sec)
```
Now the two queries have similar execution times. They both use `idx_uid` to find rows where `uid = 1`, then sort the matching rows by `ctime`.

# Index on ORDER BY Column?
From the results, people saying this is missing index on time column are just wrong. 

We do have an index on `ctime`. In fact, that index is what allows MySQL to choose the bad plan: scan `idx_ctime` backward, filter by `uid`, and stop when it finds the first matching row.

So the issue is not simply “missing index on the `ORDER BY` column.” The issue is that `ORDER BY ... LIMIT 1` changes the optimizer’s incentives.

# Well, what's the real solution?
Use composite index on `(uid, ctime)`. This index can be used to both filter by `uid` and sort by `ctime`,
because `uid` is fixed by the `WHERE` clause, MySQL can scan the `uid = 1` portion of the index in `ctime` order.
Let's see how it changes the execution plan:
```text
mysql> ALTER TABLE orders ADD INDEX idx_user_ctime (uid, ctime);
Query OK, 0 rows affected (0.675 sec)
Records: 0  Duplicates: 0  Warnings: 0

mysql> EXPLAIN SELECT id, uid FROM orders WHERE uid = 1 ORDER BY ctime DESC LIMIT 1;
+--------------------------------------------------------------------------------------------+
| EXPLAIN                                                                                    |
+--------------------------------------------------------------------------------------------+
| -> Limit: 1 row(s)  (cost=50840 rows=1)
    -> Covering index lookup on orders using idx_user_ctime (uid = 1) (reverse)  (cost=50840 rows=499861)
|
+--------------------------------------------------------------------------------------------+
1 row in set (0.001 sec)

mysql> SELECT id, uid FROM orders WHERE uid = 1 ORDER BY ctime DESC LIMIT 1;
+--------+------+
| id     | uid  |
+--------+------+
| 400000 |    1 |
+--------+------+
1 row in set (0.004 sec)
```
See? 0.004 seconds!

The original post also mentioned you can force index:
```sql
SELECT id, uid FROM orders FORCE INDEX (idx_uid) WHERE uid = 1 ORDER BY ctime DESC LIMIT 1;
```
But it's less ideal.
