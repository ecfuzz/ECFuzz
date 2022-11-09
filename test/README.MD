# test

> This directory stores unit tests for codes in src.

## execute all unit tests

```bash
python performAllTests.py
```

## generate dynamic call graphs by graphviz+pycallgraph

```bash
python generateCallGraphs.py
```

### dependency

graphviz下载

http://www.graphviz.org/download/

python-related

```bash
conda install python-graphviz

pip install pycallgraph
```

## collect coverage by coverage

```bash
python measureCoverage.py
```

### dependency
```bash
pip install coverage
```
