# Exercise 4: Conformance with token replay

This exercise consists of defining a new function called `fitness_token_replay(log, model)` which computes the conformance using the token replay approach according to the paper [Conformance checking of processes based on monitoring real behavior](https://doi.org/10.1016/j.is.2007.07.001) (cf. Metric 3 in the paper) and Section 8.2 of the [Process Mining book](https://link.springer.com/chapter/10.1007/978-3-662-49851-4_8).

In addition, the paper also summarizes the previous exercises as it also requires the following functions: `read_from_file(filename)` and `alpha(log)` which, in turn, require the definition of Petri net. Please, consider that the implementation of the Petri net can be changed to accomodate and simplify the definition of `fitness_token_replay`.

The functions will be tested against two logs as follows:

```py
log = read_from_file("extension-log-4.xes")
log_noisy = read_from_file("extension-log-noisy-4.xes")

mined_model = alpha(log)
print(round(fitness_token_replay(log, mined_model), 5))
print(round(fitness_token_replay(log_noisy, mined_model), 5))
```

And the following output should be produced:

```plain
1.0
0.95543
```

For debugging the assignment, please consider the following intermediate values for file `extension-log-4.xes`:

- <record issue, inspection, action not required, issue completion>
m = 0.0; c = 5.0; r = 0.0; p = 5.0
- <record issue, inspection, intervention authorization, work mandate, work completion, issue completion>
m = 0.0; c = 7.0; r = 0.0; p = 7.0
- <record issue, inspection, intervention authorization, no concession, issue completion>
m = 0.0; c = 6.0; r = 0.0; p = 6.0

And these are the values for `extension-log-noisy-4.xes`:

- <record issue, inspection, action not required, issue completion>
m = 0.0; c = 5.0; r = 0.0; p = 5.0
- <record issue, inspection, intervention authorization, work mandate, work completion, issue completion>
m = 0.0; c = 7.0; r = 0.0; p = 7.0
- <record issue, issue completion, issue completion, inspection, action not required>
m = 2.0; c = 6.0; r = 2.0; p = 6.0
- <record issue, inspection, issue completion>
m = 1.0; c = 4.0; r = 1.0; p = 4.0
- <record issue, inspection, action not required, action not required, issue completion>
m = 1.0; c = 6.0; r = 1.0; p = 6.0
- <record issue, inspection, intervention authorization, no concession, issue completion>
m = 0.0; c = 6.0; r = 0.0; p = 6.0
- <inspection, intervention authorization, no concession, issue completion>
m = 1.0; c = 5.0; r = 1.0; p = 5.0
- <record issue, inspection, intervention authorization, work mandate, work completion>
m = 1.0; c = 6.0; r = 1; p = 6.0
- <record issue, inspection, inspection, intervention authorization, no concession, issue completion>
m = 1.0; c = 7.0; r = 1.0; p = 7.0
- <record issue, inspection, intervention authorization, issue completion>
m = 1.0; c = 5.0; r = 1.0; p = 5.0
- <inspection, action not required, issue completion>
m = 1.0; c = 4.0; r = 1.0; p = 4.0
- <record issue, work completion, work completion, inspection, intervention authorization, work mandate, issue completion>
m = 2.0; c = 8.0; r = 2.0; p = 8.0
- <record issue, inspection, intervention authorization, issue completion, issue completion, no concession>
m = 2.0; c = 7.0; r = 2.0; p = 7.0
- <record issue, inspection, action not required, issue completion, issue completion>
m = 1.0; c = 6.0; r = 1.0; p = 6.0
- <intervention authorization, inspection, inspection, work mandate, work completion, issue completion>
m = 3.0; c = 7.0; r = 3.0; p = 7.0
- <record issue, inspection, issue completion, issue completion, intervention authorization, no concession>
m = 2.0; c = 7.0; r = 2.0; p = 7.0
- <record issue, action not required, inspection, inspection, issue completion>
m = 2.0; c = 6.0; r = 2.0; p = 6.0
- <record issue, inspection, no concession, issue completion>
m = 1.0; c = 5.0; r = 1.0; p = 5.0
- <record issue, inspection, intervention authorization, work mandate, work completion, issue completion, issue completion>
m = 1.0; c = 8.0; r = 1.0; p = 8.0
- <record issue, inspection, inspection, action not required, issue completion>
m = 1.0; c = 6.0; r = 1.0; p = 6.0
- <record issue, inspection, intervention authorization, work mandate, issue completion>
m = 1.0; c = 6.0; r = 1.0; p = 6.0
- <record issue, inspection, issue completion, issue completion, action not required>
m = 2.0; c = 6.0; r = 2.0; p = 6.0
- <inspection, intervention authorization, work mandate, work completion, issue completion>
m = 1.0; c = 6.0; r = 1.0; p = 6.0
- <record issue, work mandate, inspection, inspection, intervention authorization, intervention authorization, work completion, issue completion>
m = 2.0; c = 9.0; r = 2.0; p = 9.0
- <record issue, intervention authorization, intervention authorization, inspection, no concession, issue completion>
m = 2.0; c = 7.0; r = 2.0; p = 7.0
- <record issue, inspection, action not required>
m = 1.0; c = 4.0; r = 1; p = 4.0
- <record issue, work mandate, work mandate, inspection, intervention authorization, issue completion, issue completion, work completion>
m = 4.0; c = 9.0; r = 4.0; p = 9.0
- <record issue, action not required, action not required, inspection, issue completion>
m = 2.0; c = 6.0; r = 2.0; p = 6.0
- <record issue, intervention authorization, inspection, inspection, no concession, issue completion>
m = 2.0; c = 7.0; r = 2.0; p = 7.0
- <record issue, intervention authorization, intervention authorization, inspection, work mandate, work completion, issue completion>
m = 2.0; c = 8.0; r = 2.0; p = 8.0
- <record issue, inspection, intervention authorization, work mandate, work mandate, work completion, issue completion>
m = 1.0; c = 8.0; r = 1.0; p = 8.0
- <record issue, work mandate, work mandate, inspection, intervention authorization, work completion, issue completion>
m = 2.0; c = 8.0; r = 2.0; p = 8.0
- <record issue, action not required, issue completion>
m = 1.0; c = 4.0; r = 1.0; p = 4.0
- <record issue, inspection, work mandate, work completion, issue completion>
m = 1.0; c = 6.0; r = 1.0; p = 6.0
- <record issue, intervention authorization, work mandate, work completion, issue completion>
m = 1.0; c = 6.0; r = 1.0; p = 6.0
- <inspection, issue completion>
m = 2.0; c = 3.0; r = 2.0; p = 3.0
- <record issue, inspection, intervention authorization, work completion, issue completion>
m = 1.0; c = 6.0; r = 1.0; p = 6.0
- <record issue, inspection, intervention authorization, no concession, no concession, issue completion>
m = 1.0; c = 7.0; r = 1.0; p = 7.0
- <record issue, inspection, intervention authorization, work completion, work mandate, issue completion>
m = 1.0; c = 7.0; r = 1.0; p = 7.0
- <record issue, inspection, intervention authorization, no concession>
m = 1.0; c = 5.0; r = 1; p = 5.0
- <record issue, inspection, intervention authorization, work mandate, work completion, work completion, issue completion>
m = 1.0; c = 8.0; r = 1.0; p = 8.0
- <record issue, record issue, action not required, inspection, inspection, issue completion>
m = 2.0; c = 7.0; r = 2.0; p = 7.0
- <record issue, inspection, issue completion, issue completion, intervention authorization, intervention authorization, no concession>
m = 3.0; c = 8.0; r = 3.0; p = 8.0
- <record issue, record issue, inspection, intervention authorization, work mandate, work completion, issue completion>
m = 1.0; c = 8.0; r = 1.0; p = 8.0
- <record issue, intervention authorization, no concession, issue completion>
m = 1.0; c = 5.0; r = 1.0; p = 5.0
- <inspection, record issue, action not required, issue completion>
m = 1.0; c = 5.0; r = 1.0; p = 5.0
- <record issue, intervention authorization, work mandate, work completion, work completion, issue completion>
m = 2.0; c = 7.0; r = 2.0; p = 7.0
- <inspection, record issue, record issue, action not required, issue completion>
m = 2.0; c = 6.0; r = 2.0; p = 6.0
- <record issue, record issue, inspection, intervention authorization, no concession, issue completion>
m = 1.0; c = 7.0; r = 1.0; p = 7.0
- <record issue, inspection, intervention authorization, work completion, work mandate, work mandate, issue completion>
m = 2.0; c = 8.0; r = 2.0; p = 8.0
- <record issue, inspection, inspection, intervention authorization, work mandate, work completion, issue completion>
m = 1.0; c = 8.0; r = 1.0; p = 8.0
- <inspection, action not required, record issue, record issue, issue completion>
m = 2.0; c = 6.0; r = 2.0; p = 6.0
- <record issue, inspection, work completion, work completion, intervention authorization, work mandate, issue completion>
m = 2.0; c = 8.0; r = 2.0; p = 8.0
- <inspection, record issue, record issue, intervention authorization, no concession, issue completion>
m = 2.0; c = 7.0; r = 2.0; p = 7.0
- <record issue, record issue, inspection, action not required, issue completion>
m = 1.0; c = 6.0; r = 1.0; p = 6.0
- <record issue, no concession, no concession, inspection, intervention authorization, issue completion>
m = 2.0; c = 7.0; r = 2.0; p = 7.0
- <record issue, inspection, intervention authorization, work mandate, issue completion, issue completion, work completion>
m = 2.0; c = 8.0; r = 2.0; p = 8.0
- <record issue, inspection, intervention authorization, no concession, issue completion, issue completion>
m = 1.0; c = 7.0; r = 1.0; p = 7.0
- <record issue, intervention authorization, work mandate, work completion, inspection, inspection, issue completion>
m = 2.0; c = 8.0; r = 2.0; p = 8.0
- <record issue, inspection, no concession, no concession, intervention authorization, issue completion>
m = 2.0; c = 7.0; r = 2.0; p = 7.0
- <record issue, inspection, intervention authorization, work mandate>
m = 1.0; c = 5.0; r = 1; p = 5.0
- <record issue, intervention authorization, inspection, inspection, work mandate, work completion, issue completion>
m = 2.0; c = 8.0; r = 2.0; p = 8.0
- <record issue, inspection, intervention authorization, work completion, work completion, work mandate, issue completion>
m = 2.0; c = 8.0; r = 2.0; p = 8.0
- <record issue, inspection, intervention authorization, intervention authorization, work mandate, work completion, issue completion>
m = 1.0; c = 8.0; r = 1.0; p = 8.0
- <record issue, inspection>
m = 1.0; c = 3.0; r = 1; p = 3.0
- <record issue, issue completion, issue completion, inspection, intervention authorization, work mandate, work completion>
m = 2.0; c = 8.0; r = 2.0; p = 8.0
- <record issue, issue completion, issue completion, inspection, intervention authorization, no concession>
m = 2.0; c = 7.0; r = 2.0; p = 7.0
- <inspection, intervention authorization, work mandate, record issue, record issue, work completion, issue completion>
m = 2.0; c = 8.0; r = 2.0; p = 8.0
