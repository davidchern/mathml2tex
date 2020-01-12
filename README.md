# mathml2tex

Convert mathml back into math-tex, but with only a subset of mathml specs is supported (yet extending it is simple).

Run on Python 2.7

### Requirement

BeautifulSoup 4

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
