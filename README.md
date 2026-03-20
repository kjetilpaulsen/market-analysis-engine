# market-analysis-engine

This is an old project, but early in March 2026 I started migrating the old code into this repo. I am combining it with my python-project-blueprint repo in order to harden the surrounding infrastructure in the app. As a result not all features have been migrated yet, and the README.md is lacking. My first priority is to get the README.md up and running, which should be by 23 March 2026

A tool that stores financial data in PostgreSQL. Different analysis methods can then be used on the data.

## Features
- Two entrypoints, CLI/FastAPI
- Structured logging
- XDG folder structure
- Linear regression analysis
- Displaying of stock data based on given time period, e.g. "3y"

## Installation

### Requirements
- Python >= 3.x

### Setup
```bash
git clone https://github.com/kjetilpaulsen/market-analysis-engine.git
cd market-analysis-engine
```
