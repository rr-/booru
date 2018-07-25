import sqlalchemy as sa
from szurubooru.model.base import Base
from szurubooru.model.comment import Comment


class PostFeature(Base):
    __tablename__ = 'post_feature'

    post_feature_id = sa.Column('id', sa.Integer, primary_key=True)
    post_id = sa.Column(
        'post_id',
        sa.Integer,
        sa.ForeignKey('post.id'),
        nullable=False,
        index=True)
    user_id = sa.Column(
        'user_id',
        sa.Integer,
        sa.ForeignKey('user.id'),
        nullable=False,
        index=True)
    time = sa.Column('time', sa.DateTime, nullable=False)

    post = sa.orm.relationship('Post')  # type: Post
    user = sa.orm.relationship(
        'User',
        backref=sa.orm.backref(
            'post_features', cascade='all, delete-orphan'))


class PostScore(Base):
    __tablename__ = 'post_score'

    post_id = sa.Column(
        'post_id',
        sa.Integer,
        sa.ForeignKey('post.id'),
        primary_key=True,
        nullable=False,
        index=True)
    user_id = sa.Column(
        'user_id',
        sa.Integer,
        sa.ForeignKey('user.id'),
        primary_key=True,
        nullable=False,
        index=True)
    time = sa.Column('time', sa.DateTime, nullable=False)
    score = sa.Column('score', sa.Integer, nullable=False)

    post = sa.orm.relationship('Post')
    user = sa.orm.relationship(
        'User',
        backref=sa.orm.backref('post_scores', cascade='all, delete-orphan'))


class PostFavorite(Base):
    __tablename__ = 'post_favorite'

    post_id = sa.Column(
        'post_id',
        sa.Integer,
        sa.ForeignKey('post.id'),
        primary_key=True,
        nullable=False,
        index=True)
    user_id = sa.Column(
        'user_id',
        sa.Integer,
        sa.ForeignKey('user.id'),
        primary_key=True,
        nullable=False,
        index=True)
    time = sa.Column('time', sa.DateTime, nullable=False)

    post = sa.orm.relationship('Post')
    user = sa.orm.relationship(
        'User',
        backref=sa.orm.backref('post_favorites', cascade='all, delete-orphan'))


class PostNote(Base):
    __tablename__ = 'post_note'

    post_note_id = sa.Column('id', sa.Integer, primary_key=True)
    post_id = sa.Column(
        'post_id',
        sa.Integer,
        sa.ForeignKey('post.id'),
        nullable=False,
        index=True)
    polygon = sa.Column('polygon', sa.PickleType, nullable=False)
    text = sa.Column('text', sa.UnicodeText, nullable=False)

    post = sa.orm.relationship('Post')


class PostRelation(Base):
    __tablename__ = 'post_relation'

    parent_id = sa.Column(
        'parent_id',
        sa.Integer,
        sa.ForeignKey('post.id'),
        primary_key=True,
        nullable=False,
        index=True)
    child_id = sa.Column(
        'child_id',
        sa.Integer,
        sa.ForeignKey('post.id'),
        primary_key=True,
        nullable=False,
        index=True)

    def __init__(self, parent_id: int, child_id: int) -> None:
        self.parent_id = parent_id
        self.child_id = child_id


class PostTag(Base):
    __tablename__ = 'post_tag'

    post_id = sa.Column(
        'post_id',
        sa.Integer,
        sa.ForeignKey('post.id'),
        primary_key=True,
        nullable=False,
        index=True)
    tag_id = sa.Column(
        'tag_id',
        sa.Integer,
        sa.ForeignKey('tag.id'),
        primary_key=True,
        nullable=False,
        index=True)

    def __init__(self, post_id: int, tag_id: int) -> None:
        self.post_id = post_id
        self.tag_id = tag_id


class Post(Base):
    __tablename__ = 'post'

    SAFETY_SAFE = 'safe'
    SAFETY_SKETCHY = 'sketchy'
    SAFETY_UNSAFE = 'unsafe'

    TYPE_IMAGE = 'image'
    TYPE_ANIMATION = 'animation'
    TYPE_VIDEO = 'video'
    TYPE_FLASH = 'flash'

    FLAG_LOOP = 'loop'

    # basic meta
    post_id = sa.Column('id', sa.Integer, primary_key=True)
    user_id = sa.Column(
        'user_id',
        sa.Integer,
        sa.ForeignKey('user.id', ondelete='SET NULL'),
        nullable=True,
        index=True)
    version = sa.Column('version', sa.Integer, default=1, nullable=False)
    creation_time = sa.Column('creation_time', sa.DateTime, nullable=False)
    last_edit_time = sa.Column('last_edit_time', sa.DateTime)
    safety = sa.Column('safety', sa.Unicode(32), nullable=False)
    source = sa.Column('source', sa.Unicode(200))
    flags = sa.Column('flags', sa.PickleType, default=None)

    # content description
    type = sa.Column('type', sa.Unicode(32), nullable=False)
    checksum = sa.Column('checksum', sa.Unicode(64), nullable=False)
    file_size = sa.Column('file_size', sa.Integer)
    canvas_width = sa.Column('image_width', sa.Integer)
    canvas_height = sa.Column('image_height', sa.Integer)
    mime_type = sa.Column('mime-type', sa.Unicode(32), nullable=False)

    # foreign tables
    user = sa.orm.relationship('User')
    tags = sa.orm.relationship('Tag', backref='posts', secondary='post_tag')
    relations = sa.orm.relationship(
        'Post',
        secondary='post_relation',
        primaryjoin=post_id == PostRelation.parent_id,
        secondaryjoin=post_id == PostRelation.child_id, lazy='joined',
        backref='related_by')
    features = sa.orm.relationship(
        'PostFeature', cascade='all, delete-orphan', lazy='joined')
    scores = sa.orm.relationship(
        'PostScore', cascade='all, delete-orphan', lazy='joined')
    favorited_by = sa.orm.relationship(
        'PostFavorite', cascade='all, delete-orphan', lazy='joined')
    notes = sa.orm.relationship(
        'PostNote', cascade='all, delete-orphan', lazy='joined')
    comments = sa.orm.relationship('Comment', cascade='all, delete-orphan')

    # dynamic columns
    tag_count = sa.orm.column_property(
        sa.sql.expression.select(
            [sa.sql.expression.func.count(PostTag.tag_id)])
        .where(PostTag.post_id == post_id)
        .correlate_except(PostTag))

    canvas_area = sa.orm.column_property(canvas_width * canvas_height)
    canvas_aspect_ratio = sa.orm.column_property(
        sa.sql.expression.func.cast(canvas_width, sa.Float) /
        sa.sql.expression.func.cast(canvas_height, sa.Float))

    @property
    def is_featured(self) -> bool:
        featured_post = (
            sa.orm.object_session(self)
            .query(PostFeature)
            .order_by(PostFeature.time.desc())
            .first())
        return featured_post and featured_post.post_id == self.post_id

    score = sa.orm.column_property(
        sa.sql.expression.select(
            [sa.sql.expression.func.coalesce(
                sa.sql.expression.func.sum(PostScore.score), 0)])
        .where(PostScore.post_id == post_id)
        .correlate_except(PostScore))

    favorite_count = sa.orm.column_property(
        sa.sql.expression.select(
            [sa.sql.expression.func.count(PostFavorite.post_id)])
        .where(PostFavorite.post_id == post_id)
        .correlate_except(PostFavorite))

    last_favorite_time = sa.orm.column_property(
        sa.sql.expression.select(
            [sa.sql.expression.func.max(PostFavorite.time)])
        .where(PostFavorite.post_id == post_id)
        .correlate_except(PostFavorite))

    feature_count = sa.orm.column_property(
        sa.sql.expression.select(
            [sa.sql.expression.func.count(PostFeature.post_id)])
        .where(PostFeature.post_id == post_id)
        .correlate_except(PostFeature))

    last_feature_time = sa.orm.column_property(
        sa.sql.expression.select(
            [sa.sql.expression.func.max(PostFeature.time)])
        .where(PostFeature.post_id == post_id)
        .correlate_except(PostFeature))

    comment_count = sa.orm.column_property(
        sa.sql.expression.select(
            [sa.sql.expression.func.count(Comment.post_id)])
        .where(Comment.post_id == post_id)
        .correlate_except(Comment))

    last_comment_creation_time = sa.orm.column_property(
        sa.sql.expression.select(
            [sa.sql.expression.func.max(Comment.creation_time)])
        .where(Comment.post_id == post_id)
        .correlate_except(Comment))

    last_comment_edit_time = sa.orm.column_property(
        sa.sql.expression.select(
            [sa.sql.expression.func.max(Comment.last_edit_time)])
        .where(Comment.post_id == post_id)
        .correlate_except(Comment))

    note_count = sa.orm.column_property(
        sa.sql.expression.select(
            [sa.sql.expression.func.count(PostNote.post_id)])
        .where(PostNote.post_id == post_id)
        .correlate_except(PostNote))

    relation_count = sa.orm.column_property(
        sa.sql.expression.select(
            [sa.sql.expression.func.count(PostRelation.child_id)])
        .where(
            (PostRelation.parent_id == post_id) |
            (PostRelation.child_id == post_id))
        .correlate_except(PostRelation))

    __mapper_args__ = {
        'version_id_col': version,
        'version_id_generator': False,
    }
