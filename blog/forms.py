from django import forms
from blog.models import Article


class AddArticleForm(forms.ModelForm):
    cover = forms.ImageField(required=False)

    class Meta:
        model = Article

        fields = ['title', 'content', 'category']

    def clean_title(self):
        title    = self.cleaned_data.get('title')

        if len(title.strip()) < 6:
            self.add_error('title', 'The title is too short.')

        title = title.strip()

        return title

    def clean_content(self):
        content = self.cleaned_data.get('content')

        if len(content) < 20:
            self.add_error('content', 'The content is too short.')

        return content

    def clean_category(self):
        category = self.cleaned_data.get('category')

        return category


class ImageArticleForm(forms.Form):
    image = forms.ImageField(required=False)