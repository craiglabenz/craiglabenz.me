import datetime

# Django
from django.db import models
from django.core.urlresolvers import reverse
from django.utils.text import slugify

# 3rd Party
from markdown import markdown
from taggit.managers import TaggableManager

# Local
from blog.querysets import EntryQuerySet
from core.models import BaseModel
from core.utils import zero_pad


class Category(BaseModel):
    title = models.CharField(max_length=250, help_text='Maximum 250 characters.')
    slug = models.SlugField(unique=True, help_text="Suggested value automatically generated from title. Must be unique.")
    description = models.TextField()

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['title']

    def live_entries(self):
        return self.entries.live()

    def as_str(self):
        return self.title

    def get_absolute_url(self):
        return reverse('entries_by_category', kwargs={'slug': self.slug})


class Entry(BaseModel):

    LIVE = 1
    DRAFT = 2
    HIDDEN = 3
    STATUS_CHOICES = (
        (LIVE, 'Live'),
        (DRAFT, 'Draft'),
        (HIDDEN, 'Hidden'),
    )

    # Core fields
    title = models.CharField(max_length=250)
    excerpt = models.TextField(blank=True)
    body = models.TextField()
    published_on = models.DateField(default=datetime.date.today)

    # Fields to store generated HTML.
    excerpt_html = models.TextField(editable=False, blank=True)
    body_html = models.TextField(editable=False, blank=True)

    enable_comments = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    slug = models.SlugField(unique_for_date='published_on')
    status = models.IntegerField(choices=STATUS_CHOICES, default=DRAFT)

    categories = models.ManyToManyField(Category, related_name="entries")
    tags = TaggableManager(blank=True)

    objects = EntryQuerySet.as_manager()

    class Meta:
        verbose_name = "Entry"
        verbose_name_plural = "Entries"

    def as_str(self):
        return self.title

    def formatted_date_str(self):
        weekday_map = {
            0: 'Monday',
            1: 'Tuesday',
            2: 'Wednesday',
            3: 'Thursday',
            4: 'Friday',
            5: 'Saturday',
            6: 'Sunday',
        }

        month_map = {
            1: 'January',
            2: 'February',
            3: 'March',
            4: 'April',
            5: 'May',
            6: 'June',
            7: 'July',
            8: 'August',
            9: 'September',
            10: 'October',
            11: 'November',
            12: 'December',
        }

        return "{day_of_week} {day} {month} {year}".format(
            day_of_week=weekday_map[self.published_on.weekday()],
            month=month_map[self.published_on.month],
            day=zero_pad(self.published_on.day, 2),
            year=self.published_on.year
        ).upper()

    @property
    def snippets_dict(self):
        return self.get_snippets_as_dict()

    def get_snippets_as_dict(self):
        if not hasattr(self, '_snippets_dict'):
            self._snippets_dict = {}
            for snippet in self.snippets.all():
                self._snippets_dict[snippet.slug] = snippet
                self._snippets_dict[snippet.title] = snippet
        return self._snippets_dict

    def save(self, **kwargs):
        self.format_markdown()
        super().save(**kwargs)

    def format_markdown(self):
        self.body_html = markdown(self.body)
        self.excerpt_html = markdown(self.excerpt)

    def get_absolute_url(self):
        return reverse('blog_entry_detail', kwargs={
            'year': self.published_on.strftime("%Y"),
            'month': self.published_on.strftime("%m"),
            'day': self.published_on.strftime("%d"),
            'slug': self.slug
        })


class Language(BaseModel):
    name = models.CharField(max_length=50)
    prism_tag = models.CharField(max_length=50, verbose_name="PRISM Tag")

    class Meta:
        verbose_name = "Language"
        verbose_name_plural = "Languages"

    def as_str(self):
        return self.name


class Snippet(BaseModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, help_text="Will be generated if left blank.")

    language = models.ForeignKey(Language, related_name="snippets")
    code = models.TextField()

    entry = models.ForeignKey(Entry, related_name="snippets")

    class Meta:
        verbose_name = "Snippet"
        verbose_name_plural = "Snippets"

    def as_str(self):
        return self.title

    def save(self, **kwargs):
        self.ensure_slug()
        super().save(**kwargs)

    def ensure_slug(self):
        if not self.slug:
            self.slug = slugify(self.title)

    def get_prepared_code(self):
        code = self.code

        # Language-specific prism gotchas
        if self.language.prism_tag == "markup":
            code = code.replace("<", "&lt;")

        return code


class TagColor(BaseModel):

    tag_name = models.CharField(max_length=50, unique=True, verbose_name="Tag Name")
    color_hex = models.CharField(max_length=6, verbose_name="Color Hex")
    text_color = models.CharField(max_length=6, default="fff", blank=True, verbose_name="Text Color")

    class Meta:
        verbose_name = "Tag Color"
        verbose_name_plural = "Tag Colors"

    def as_str(self):
        return self.tag_name

    def save(self, **kwargs):
        self.ensure_text_color()
        super().save(**kwargs)

    def ensure_text_color(self):
        if not self.text_color:
            self.text_color = "fff"

    def get_absolute_url(self):
        return reverse("entries_by_tag", kwargs={"tag_name": self.tag_name})
