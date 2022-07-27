# totp
TOTP

-g filename.key      File with the string to use. Content can be in hex or base32\
-t <type>            Select the type of string contained in the file <filename.key>\
                       type    => base32|hex\
                       default => base32\
-g filename.key -P   It requests a password to encrypt the content of the filename.key\
-gk filename.key     Generate OTP, this mode don´t store any information\
-gkf filename.key    Generate random passphrase in base32\
-gkP                 Generate random password for encryption data\
-k                   Generate OTP\
-k -P                Request password for decryption\
-s seconds           TOTP time-step duration (default=`30`)\
-d digits            Number of digits in one-time-password\
-q                   Show info stored in database\
-a algorithm         Support values are sha1, sha256, sha512 (default sha1)\
-S service           Name of the service where otp will be used, default totp\
-h                   Show help

* Configuration file: ./totp.cfg, /etc/totp/totp.cfg

* Usage:\
--   Generate OTP using filename.key\
./{0} -gk filename.key [-t <base32|hex>] [-a <sha1|sha256|sha512>]\
--   Save key into database\
./{0} -g filename.key -S service [-P] [-t <base32|hex>]\
--   Generate OTP using database\
./{0} -k -S service [-P] [-s <seconds>] [-d <digits>] [-a <sha1|sha256|sha512>]\
--   Consult the information stored in the database\
./{0} -q [-S service]
