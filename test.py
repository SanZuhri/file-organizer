# Given a password string, return "weak", "medium", or "strong" based on the strength of the password.

# A password is evaluated according to the following rules:

# It is at least 8 characters long.
# It contains both uppercase and lowercase letters.
# It contains at least one number.
# It contains at least one special character from this set: !, @, #, $, %, ^, &, or *.
# Return "weak" if the password meets fewer than two of the rules. Return "medium" if the password meets 2 or 3 of the rules. Return "strong" if the password meets all 4 rules.

# Waiting:1. check_strength("123456") should return "weak".
# Waiting:2. check_strength("pass!!!") should return "weak".
# Waiting:3. check_strength("Qwerty") should return "weak".
# Waiting:4. check_strength("PASSWORD") should return "weak".
# Waiting:5. check_strength("PASSWORD!") should return "medium".
# Waiting:6. check_strength("PassWord%^!") should return "medium".
# Waiting:7. check_strength("qwerty12345") should return "medium".
# Waiting:8. check_strength("PASSWORD!") should return "medium".
# Waiting:9. check_strength("PASSWORD!") should return "medium".
# Waiting:10. check_strength("S3cur3P@ssw0rd") should return "strong".
# Waiting:11. check_strength("C0d3&Fun!") should return "strong".

def check_strength(password):  
    if 
