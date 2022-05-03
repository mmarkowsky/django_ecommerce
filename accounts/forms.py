from django import forms
from accounts.models import Account


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        "placeholder": "Ingresse senha"
    }))

    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        "placeholder": "Reingresse senha"
    }))

    class Meta:
        model = Account
        fields = ["first_name", "last_name",
                  "phone_number", "email", "password"]

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields["first_name"].widget.attrs["placeholder"] = "Ingresse seu nombre"
        self.fields["last_name"].widget.attrs["placeholder"] = "Ingresse seu apellido"
        self.fields["phone_number"].widget.attrs["placeholder"] = "Ingresse seu telefone"
        self.fields["email"].widget.attrs["placeholder"] = "Ingresse seu email"
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"

    def clean(self):
        cleaned_data = super(RegistrationForm,self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError(
                "As senhas não coicidem"
            )

