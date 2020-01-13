# mathml2tex

Convert MathML back into Math-Tex, but with only a subset of MathML syntaxes is supported (yet extending it is quite simple).

Run on Python 2.7, may run on Python 3.x too.

### Requirement

BeautifulSoup 4. To install it, just run

```shell
pip install bs4
```

### Usage

```python
from mathml2tex import MathMLTeX

m = MathMLTeX()

xml = '''<math xmlns="http://www.w3.org/1998/Math/MathML">
      <msqrt>
        <mn>2</mn>
      </msqrt>
    </math>'''

m.convert(xml) # -> '\\sqrt{2}'
```
