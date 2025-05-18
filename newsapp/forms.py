from django import forms

from newsapp.models import Article


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = [
            'name',
            'desc',
            'img',
        ]

    def __init__(self, *args, **kwargs):
        super(ArticleForm, self).__init__(*args, **kwargs)
        self.fields['desc'].widget.attrs.update({
            'placeholder': 'Введите ваше описание',
            'rows': 3,
            'class': 'tinymce'
        })
        self.fields['name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите название статьи'
        })
        self.fields['img'].widget.attrs.update({
            'class': 'form-control'
        })
        

class ArticleEditForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['name', 'desc', 'img']
        widgets = {
        
            'desc': forms.Textarea(attrs={
                'placeholder': 'Введите ваше описание',
                'rows': 3,
                'class': 'tinymce form-control'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название статьи'
            }),
            'img': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Убираем подсказки для всех полей
        for field in self.fields.values():
            field.help_text = ''