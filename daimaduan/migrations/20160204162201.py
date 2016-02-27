import re
from mongodb_migrations.base import BaseMigration


ALL_SUPPORTTED_SYNTAX = (
    ('bash', 'Bash'),
    ('java', 'Java'),
    ('cpp', 'C++'),
    ('xml', 'XML'),
    ('spec', 'RPMSpec'),
    ('sql', 'SQL'),
    ('json', 'JSON'),
    ('sass', 'Sass'),
    ('coffee-script', 'CoffeeScript'),
    ('vim', 'VimL'),
    ('scala', 'Scala'),
    ('css', 'CSS'),
    ('matlab', 'Matlab'),
    ('c', 'C'),
    ('yaml', 'YAML'),
    ('text', 'Text only'),
    ('dart', 'Dart'),
    ('diff', 'Diff'),
    ('swift', 'Swift'),
    ('js', 'JavaScript'),
    ('puppet', 'Puppet'),
    ('groovy', 'Groovy/Gradle'),
    ('python', 'Python'),
    ('scss', 'SCSS'),
    ('lua', 'Lua'),
    ('go', 'Go'),
    ('perl', 'Perl'),
    ('ini', 'INI'),
    ('nginx', 'Nginx configuration file'),
    ('php', 'PHP'),
    ('erb', 'ERB'),
    ('html', 'HTML'),
    ('rst', 'reStructuredText'),
    ('make', 'Makefile'),
    ('rb', 'Ruby'),
    ('kotlin', 'Kotlin'),
    ('clojure', 'Clojure'),
    ('csharp', 'C#'),
    ('objective-c', 'Objective-C'),
)

OLD_SYNTAX_NEW_SYNTAX = {
    'less': 'CSS',
    'access-log': 'Text only',
    'vim-script': 'VimL',
    'gradle': 'Groovy',
    'nginx': 'Nginx configuration file',
    'text': 'Text only'
}


class Migration(BaseMigration):
    def upgrade(self):
        """
        1. get all codes
        2. set codes into pastes
        3. add key to tag
        :return:
        """
        new_syntax_keys = [syntax[0] for syntax in ALL_SUPPORTTED_SYNTAX]

        self.db.syntax.drop()
        for syntax in ALL_SUPPORTTED_SYNTAX:
            self.db.syntax.save({'key': syntax[0], 'name': syntax[1]})

        codes = {}
        for code in self.db.code.find():
            codes[str(code['_id'])] = code
        self.db.code.drop()

        self.db.tag.drop()

        user_likes = {}
        for like in self.db.like.find():
            paste = self.db.paste.find_one({'_id': like['Paste']['_ref'].id})
            user_id = str(like['user'])
            if user_id not in user_likes:
                user_likes[user_id] = []
            user_likes[user_id].append(paste['hash_id'])

        new_pastes = self.get_new_pastes(codes, new_syntax_keys)

        self.db.paste.drop()
        for paste in new_pastes:
            self.db.paste.save(paste)

        self.update_user_likes(user_likes)

        self.db.like.drop()
        self.db.rate.drop()

    def update_user_likes(self, user_likes):
        for user in self.db.user.find():
            user['likes'] = []
            user_id = str(user['_id'])
            if user_id in user_likes.keys():
                for paste_id in user_likes[user_id]:
                    paste = self.db.paste.find_one({'hash_id': paste_id})
                    user['likes'].append(paste['_id'])
            for i in ['favourites', 'paste_likes_count', 'pastes_count', 'watched_users', 'oauths']:
                if i in user:
                    del (user[i])
            self.db.user.save(user)

    def get_new_pastes(self, codes, new_syntax_keys):
        new_pastes = []
        for paste in self.db.paste.find():
            new_paste = {}
            new_paste['created_at'] = paste['created_at']
            new_paste['updated_at'] = paste['updated_at']
            new_paste['title'] = paste['title']
            new_paste['user'] = paste['user']
            new_paste['hash_id'] = paste['hash_id']
            new_paste['is_private'] = paste['is_private']
            new_paste['views'] = paste['views']
            new_paste['codes'] = []
            code_ids = [str(code) for code in paste['codes']]
            tags = []
            for code_id in code_ids:
                code = codes[code_id]
                if code['tag'] in new_syntax_keys:
                    syntax = self.db.syntax.find_one({'name': re.compile(code['tag'], re.IGNORECASE)})
                else:
                    if code['tag'] in OLD_SYNTAX_NEW_SYNTAX.keys():
                        syntax = self.db.syntax.find_one(
                            {'name': re.compile(OLD_SYNTAX_NEW_SYNTAX[code['tag']], re.IGNORECASE)})
                    else:
                        re_string = code['tag'].replace('+', '\+')
                        syntax = self.db.syntax.find_one({'name': re.compile(re_string, re.IGNORECASE)})
                tag = self.db.tag.find_one({'key': syntax['key']})
                if tag:
                    tags.append(tag['_id'])
                if not tag:
                    tag = self.db.tag.save({'key': syntax['key'], 'name': syntax['name']})
                    tags.append(tag)
                new_paste['codes'].append({'title': code['title'],
                                           'content': code['content'],
                                           'syntax': syntax['_id']})
            new_paste['tags'] = tags
            new_pastes.append(new_paste)
        return new_pastes

    def downgrade(self):
        print "I'm in downgrade - migration2"
