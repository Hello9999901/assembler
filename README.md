# assembler

## Basic Usage

```sh
python3 assembler.py <file.asm>
```

> Outputs out.hack in current directory

## Advanced Usage

```sh
python3 assembler.py <file.asm> && echo "\n\nDiff Comparison:" && diff out.hack <file.asm> | grep "^>" | wc -l
```

## Dependencies

- Python 3
- sys module
