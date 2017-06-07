#!/bin/bash
python create_database.py
python create_lambda_function.py
python create_cloudwatch_event.py
