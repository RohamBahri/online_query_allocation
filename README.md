# Online Query Allocation: An Empirical Study

This repository contains the implementation and analysis of online query allocation algorithms for a CMPUT 676 course project at the University of Alberta. The study is based on the framework introduced by Mahdian et al. (2012), which focuses on balancing optimistic and pessimistic strategies in online optimization.

## Overview

Online optimization involves sequential decision-making under uncertainty. This project explores the query allocation problem in online advertising, where search engines assign ad spaces to advertisers with budget constraints. The implemented algorithms aim to maximize revenue while handling prediction uncertainties.

## Algorithms
1. **Optimistic Algorithm**: Leverages offline predictions to guide query allocations.
2. **Pessimistic Algorithm**: Ensures robust allocations using competitive ratio guarantees.
3. **Balanced Algorithm**: Combines optimistic and pessimistic strategies, dynamically adapting to input variability.

## Features
- Implementation of online query allocation algorithms.
- Synthetic dataset generation with adjustable prediction error levels.
- Performance evaluation of algorithms across various scenarios.

## Experimental Setup
- **Dataset**: Synthetic data for 100 advertisers, 100 keywords, and 1,000 queries.
- **Metrics**: Total revenue compared across prediction error levels (0.0, 0.25, 0.5) and balance parameters (α values: 1.0, 2.0, 4.0, 5.0, 10.0).
- **Replications**: Experiments repeated 10 times for reliability.

## Results
The **Balanced Algorithm** outperformed in adaptability, leveraging accurate predictions while remaining robust to errors. Detailed visualizations of the results are included in the project.

