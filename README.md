# An Useless Interpreter for Lox 

In this project, I use python to create a Lox interpreter (which is super useless, but educational). 

## Roadmap

- [x] Scanning
- [ ] Parser
  - [x] Expression
  - [ ] Statement
  - [ ] Control Loop
  - [ ] Function
  - [ ] Class

## Why bother? 
Learning how to build a interpreter is a valuable experience. There are a lot of theories behind the process (Linguistic, TCS, Engineering). 

## Why python? 
The short answer is Python Rules! Well, I can build something like this in C++ also if I really want to torture myself, I can build the interpreter in C or even in Assembly. But that would require me to spend the majority of the time dealing with language limitations rather than the mechenism of interpretor itself. 

## Lox
All the file is located in one file to avoid circular import error in python. It's not that long, which shows building an interpreter is super easy to do. The whole project follow the book *"Crafting Intepreters"*. In fact, this can be consider a translation from the original JAVA implementation to Python. 

### How to run 
```
python lox.py {script}
```
It requires python, yeah, it's stupid, but it is indeed an interpretor