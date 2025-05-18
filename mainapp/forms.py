from django import forms

from mainapp.models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text', 'parent_comment']

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['text'].widget = forms.Textarea(attrs={'placeholder': 'Оставить комментарий', 'rows': 2, 'class': 'form-control'})
        self.fields['parent_comment'].widget = forms.HiddenInput()
        self.fields['text'].label = False
