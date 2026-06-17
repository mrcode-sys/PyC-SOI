class Pessoa:
  def __init__(self, nome, idade, altura):
    self.nome = nome
    self.idade = idade
    self.altura = altura

pessoa = Pessoa("Marcos", 10, 1.5)

print(pessoa.nome)
print(pessoa.idade)
print(pessoa.altura)