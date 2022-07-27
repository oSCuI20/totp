# totp
TOTP

-g filename.key      File with the string to use. Content can be in hex or base32__
-t <type>            Select the type of string contained in the file <filename.key>__
                       type    => base32|hex__
                       default => base32__
-g filename.key -P   It requests a password to encrypt the content of the filename.key__
-gk filename.key     Generate OTP, this mode don´t store any information__
-gkf filename.key    Generate random passphrase in base32__
-gkP                 Generate random password for encryption data__
-k                   Generate OTP__
-k -P                Request password for decryption__
-s seconds           TOTP time-step duration (default=`30`)__
-d digits            Number of digits in one-time-password__
-q                   Show info stored in database__
-a algorithm         Support values are sha1, sha256, sha512 (default sha1)__
-S service           Name of the service where otp will be used, default totp__
-h                   Show help__

* Configuration file: ./totp.cfg, /etc/totp/totp.cfg

* Usage:

*   Generate OTP using filename.key

** ./{0} -gk filename.key [-t <base32|hex>] [-a <sha1|sha256|sha512>]

*   Save key into database

** ./{0} -g filename.key -S service [-P] [-t <base32|hex>]

*   Generate OTP using database

** ./{0} -k -S service [-P] [-s <seconds>] [-d <digits>] [-a <sha1|sha256|sha512>]

*   Consult the information stored in the database

** ./{0} -q [-S service]
