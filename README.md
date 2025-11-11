<span align="center">
    <a href="https://huggingface.co/datasets/DataScienceUIBK/ComplexTempQA/tree/main"><img alt="Huggingface" src="https://img.shields.io/static/v1?label=Dataset&message=ComplexTempQA&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAAIGNIUk0AAHomAACAhAAA+gAAAIDoAAB1MAAA6mAAADqYAAAXcJy6UTwAAAIoUExURQAAAP/////57v/67xUVFf/clv+KAP/uzf/sxv8AAP9TAP/ltP///v/ouP/////////////////////////////8+v/pvP/biP/Vbf/Vbv/cif/qv//9+//////////03v/Yev/Zfv/14//25v/Uav/Vbv/46//////dkf/gmP/////04P/25//pvP/sxf/////lr//ouP/qwP/tyf/msv/ntf/+/P/36f/LUf/36P/w0v/w0//w0//w0//78//gm//QZv/RZv/gm//78v/////14v/nt//gnP/hn//w0f/////w0f/hn//gnP/nt//14v/////////////////LLv/MGv/PGf/LL//LG//THP/THv/SHv/UHv/LGv/LH/7SHuK8JOzDIuW+I+jAI//LHv/PTP/NF/PBG3BkOpyGMvrOH4R0NoV0NvzJGv/MF//QT//MLv/LGPu/FNayJu7FIdq2Jf7DFP/JF//ML//LJurCIsCiKujCIubAI7+hK/DHIf/LJ//HK//NGf/SHeS9IlxSP25QQmtOQmVZPu3DIf/RHf/HLP++Kf/AD/++EP3EFNCfLNhpQthrQdinKv/FFP/AEP+/K/++Dv/BEv+/Ef/CE//MIf/NIP/MGf++D//KTP/FOP/DE//PG//PHP/JGP/EFP/EM//BDf/TH//GFP/CEP/DEP/EEv/BDv/MS//IJ//JHf/JHP/JP//IQf/IHP/IJv/LSf///7SHOh0AAABUdFJOUwAAAAAAAAAAAAAAAAAABiZCQykIAUGn3/Hy4q5KAwRy7vJ/Yfb7cR/X4ipkdpepAqi5mavM2z5v/pGTtZS2QtP4999bIGyry8yUR4fJzbJ2BRIRE9ZoIHEAAAABYktHRAH/Ai3eAAAAB3RJTUUH6AIGEyohVAr+rAAAARZJREFUGNNjYGBgZGTi4xcQFBJmZmRkYQDxRUTFxCUkpaRlZBkZQXw5eYWQ0LCw0HBFJWGgCCOrskpEZFR0dExkrKoaG1BAXSMuPiExOjopOSpFU4uRgV07NS09IzMqKzsnNy9fh4OBU7egsKi4JCo6ubSsvEJPlkHfoDIqqqq6prauPiqqwVCYgcuosam5pbWtvaOzq6nbWJZBy6Snt69/wsRJk6f0TZ1masZgbjF9xsxZhbPnzJ01c8a8+ZYMVgt6F5aHLly0eGHokqVTl1kz2CxYXhi1YuWq1WuiouauXWbLYGe/bv2GjZscHDdv2bh1m5MzA7eLq5u7h6eXoLePr5+/ENDpjBwBgYH6PIyMQcF8vIyMAKnZUpQQgaV4AAAAJXRFWHRkYXRlOmNyZWF0ZQAyMDI0LTAyLTA2VDE5OjQyOjI1KzAwOjAwybP6HAAAACV0RVh0ZGF0ZTptb2RpZnkAMjAyNC0wMi0wNlQxOTo0MjoyNSswMDowMLjuQqAAAAAodEVYdGRhdGU6dGltZXN0YW1wADIwMjQtMDItMDZUMTk6NDI6MzMrMDA6MDBAgVbbAAAAAElFTkSuQmCC&color=20BEFF"/>
          <a href="https://arxiv.org/abs/2406.04866"><img src="https://img.shields.io/static/v1?label=Paper&message=ArXiv&color=green&logo=arXiv"></a>
    <a href="https://creativecommons.org/publicdomain/zero/1.0/deed.en"><img src="https://img.shields.io/static/v1?label=License&message=CC0-1.0&color=red"></a>
</span>

# ComplexTempQA

## Overview

This repository contains a large-scale temporal question answering dataset designed for evaluating and training language models on temporal reasoning tasks. The dataset consists of question-answer pairs with a focus on temporal aspects, covering a wide range of events and entities from 1987 to 2023.

<p align="center">
<img src="./src/QuestionGeneration/ExampleTimeline.png">
</p>

## Dataset Description

- **Size**: The dataset comprises **100,228,457** question-answer pairs, making it one of the largest temporal question answering datasets available.
- **Question Types**: Questions are categorized based on their complexity, including easy and hard questions, each designed to test different levels of temporal reasoning and understanding.
- **Content**: The dataset covers a diverse range of events and entities, sourced from Wikipedia and Wikidata, ensuring a rich and varied set of questions for evaluation.
- **Metadata**: Each question-answer pair includes additional metadata, such as entity/event IDs, question difficulty ratings, and temporal attributes, providing valuable information for analysis and model evaluation.

## Dataset distribution

<p align="left">
<img src="./src/QuestionGeneration/taxonomy.png">
</p>


| **Name**               | **Total**       |
|------------------------|----------------|
| Attribute Event        | 83,798         |
| Attribute Entity       | 84,079         |
| Attribute Time         | 9,454          |
| Comparison Event       | 25,353,340     |
| Comparison Entity      | 74,678,117     |
| Comparison Time        | 54,022,952     |
| Counting Event        | 18,325         |
| Counting Entity       | 10,798         |
| Counting Time         | 12,732         |
| **Multi-Hop:**         | 76,933         |
| **Unnamed Event:**     | 8,707,123      |
| **Total:**            | **100,228,457** |

## Evaluation and Usage

- **Performance Evaluation**: The dataset can be used to evaluate the performance of language models on temporal reasoning tasks, including across-time comparison, event/entity detection, and multi-hop reasoning.
- **Fine-Tuning**: Researchers can leverage this dataset for fine-tuning language models, enhancing their temporal reasoning capabilities and performance on similar tasks.

## Dataset

- **Download**: The dataset is available at [Hugging Face](https://huggingface.co/datasets/DataScienceUIBK/ComplexTempQA)
- **Testing Dataset**: A small version for testing purpose is available [here](./ComplexTempQA_small.json)


## Question Generation

This project contains Python scripts designed to generate various types of questions based on event data. The scripts read event attributes from a database, construct questions, and store them back in the database.
<p align="center">
<img src="./src/QuestionGeneration/pipeline.png">
</p>

### Requirements

- Python 3.x
- `psycopg2` for PostgreSQL database interaction
- `requests` for HTTP requests
- `configparser` for reading database configuration
- `SPARQLWrapper` for executing SPARQL queries

### Setup

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd <repository_folder>
2. Install the required Python packages:
   ```bash
   pip install psycopg2 configparser pandas
3. Configure the database connection:
   - Create a `database.ini` file with the following format:
     ```ini
     [postgresql]
     host=your_host
     database=your_database
     user=your_user
     password=your_password
     ```
### Running the Scripts

1. Ensure your database is set up and populated with the required data.
2. Run the question generation files for the desired type of question
