import sys

class GenerateAst:
    def __init__(self):
        pass
    
    def defineType(self, writer, baseName, className, fields):
        writer.write(f"class {className}({baseName}):\n")
        writer.write(f"\tdef __init__(self, {fields}):\n")
        field_names = fields.split(", ")
        for field in field_names:
            writer.write(f"\t\tself.{field} = {field}\n")
        writer.write(f"\tdef accept(self, visitor):\n")
        writer.write(f"\t\treturn visitor.visit_{className.lower()}_{baseName.lower()}(self)\n\n")
        
    def defineVisitor(self, writer, baseName, types):
        writer.write(f"class {baseName}Visitor:\n")
        for type in types:
            typeName = type.split(":")[0].strip()
            writer.write(f"\t@abstractmethod\n")
            writer.write(f"\tdef visit_{typeName.lower()}_{baseName.lower()}(self, {baseName.lower()}):\n")
            writer.write(f"\t\tpass\n\n")
    
    def defineAst(self, outputDir, baseName, types):
        try: 
            path = outputDir + '/' + baseName + '.py'
            with open(path, "w", encoding="UTF-8") as writer:
                writer.write(f"from abc import ABC, abstractmethod\n\n")
                writer.write(f"class {baseName}(ABC):\n")
                writer.write(f"\t@abstractmethod\n")
                writer.write(f"\tdef accept(self, visitor):\n")
                writer.write(f"\t\tpass\n\n")
                self.defineVisitor(writer, baseName, types)
                for type in types:
                    parts = type.split(":")
                    className = parts[0].strip()
                    fields = parts[1].strip()
                    self.defineType(writer, baseName, className, fields)
                    
        except IOError:
            print("IO exception.")
        
    def main(self, argv):
        if len(argv) != 2:
            print("Usage: generate_ast <output directory>")
            sys.exit(64)
        output_dir = argv[1]
        
        self.defineAst(output_dir, "Expr", ["Assign   : name, value",
                                            "Binary   : left, operator, right",
                                            "Call     : callee, paren, arguments",
                                            "Grouping : expression",
                                            "Literal  : value",
                                            "Logical  : left, operator, right",
                                            "Unary    : operator, right", 
                                            "Variable : name"])
        
        self.defineAst(output_dir, "Stmt", ["Block      : statements",
                                            "Expression : expression",
                                            "Function   : name, params, body",
                                            "If         : condition, thenBranch, elseBranch",
                                            "Put        : expression", 
                                            "Return     : keyword, value",
                                            "Var        : name, initializer", 
                                            "While      : condition, body"])

generateAst = GenerateAst()
generateAst.main(sys.argv)
