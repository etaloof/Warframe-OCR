from spellcheck import SpellCheck
spell_check = SpellCheck('words.txt')
string_to_be_checked = "Execptionelle"
spell_check.check(string_to_be_checked)
print(spell_check.suggestions())
print(spell_check.correct())
