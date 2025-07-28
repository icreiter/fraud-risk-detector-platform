# fraud-risk-detector-platform
詐騙風險提醒與教育平台

# Project Structure
```
fraud-alert-platform/
├── Dockerfile                  #  (待整理上傳)
├── docker-compose.yml          #  (待整理上傳)
├── requirements.txt            #  (待整理上傳)
├── README.md
├── data_sample/                # 3-5 screenshot samples & json sample
├── src/
│   ├── input_dir/              # sample screenshots for OCR
│   ├── OCR_output/             # OCR output sample results
│   ├── crawler.py              # requests + BS4 (待整理上傳)
│   ├── preprocess.py           # 去重、標籤統一、stopwords (待整理上傳)
│   ├── OCR_module.py           # PaddleOCR wrapper
│   ├── embedding.py            # CKIP-BERT encode (待整理上傳)
│   └── retrieval.py            # FAISS search (待整理上傳)
├── demo.py                     # demo the toy model (待整理上傳) 
```
