from pydantic import BaseModel, EmailStr, constr, field_validator, model_validator


class UserSchema(BaseModel):
    username: str
    email: EmailStr | None = None
    full_name: str | None = None


class UserInDBSchema(UserSchema):
    id: int
    hashed_password: str


class UserUpdateSchema(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    full_name: str | None = None


class UserRegisterSchema(UserSchema):
    password: constr(min_length=8)
    password2: str

    @model_validator(mode='after')
    def check_passwords_match(self) -> 'UserRegisterSchema':
        pw1 = self.password
        pw2 = self.password2
        if pw1 is not None and pw2 is not None and pw1 != pw2:
            raise ValueError('passwords do not match')
        return self
