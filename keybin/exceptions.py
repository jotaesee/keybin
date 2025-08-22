class KeybinError(Exception):
    pass

class SessionAlreadyExistsError(KeybinError):
    pass

class UserNotFoundError(KeybinError):
    pass

class InvalidPasswordError(KeybinError):
    pass

class NoSessionActiveError(KeybinError):
    pass

class SessionExpiredError(KeybinError):
    pass

class CorruptedSessionError(KeybinError):
    pass

class PasswordNeededError(KeybinError):
    pass

