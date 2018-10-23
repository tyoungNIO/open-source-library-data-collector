import os
import datetime
try:
    import unittest2 as unittest
except ImportError:
    import unittest
if os.environ.get('TRAVIS') is None:
    from db_connector import (DBConnector, GitHubData, PackageManagerData,
                              get_db_connection_string,)
    from config import Config
    from github import GitHub
    from package_managers import PackageManagers
    from sendgrid_email import SendGrid
try:
    basestring
except NameError:
    basestring = str


class TestConfig(unittest.TestCase):
    def setUp(self):
        if os.environ.get('TRAVIS') is None:
            self.config = Config()

    def test_initialization(self):
        if os.environ.get('TRAVIS') is None:
            github_token = os.environ.get('GITHUB_TOKEN')
            self.assertTrue(isinstance(github_token, basestring))
            sendgrid_api_key = os.environ.get('SENDGRID_API_KEY')
            self.assertTrue(isinstance(sendgrid_api_key, basestring))
            mysql_db = os.environ.get('MYSQL_DB_URL')
            self.assertTrue(isinstance(mysql_db, basestring))
            self.assertTrue(isinstance(self.config.github_user, basestring))
            self.assertTrue(isinstance(self.config.github_repos, list))
            self.assertTrue(isinstance(self.config.package_manager_urls, list))
            self.assertTrue(isinstance(self.config.to_email, basestring))
            self.assertTrue(isinstance(self.config.from_email, basestring))
            self.assertTrue(isinstance(self.config.email_subject, basestring))
            self.assertTrue(isinstance(self.config.email_body, basestring))

    def test_mysql_db_connection_string(self):
        if os.environ.get('TRAVIS'):
            return

        mysql_str = 'mysql://user:pass@host:port/dbname'
        connection_string = get_db_connection_string(mysql_str)
        self.assertEqual(connection_string,
                         'mysql+pymysql://user:pass@host:port/dbname')

    def test_sqllite_db_connection_string(self):
        if os.environ.get('TRAVIS'):
            return

        # in memory
        sqllite = 'sqlite://'
        connection_string = get_db_connection_string(sqllite)
        self.assertEqual(connection_string, 'sqlite://')

        # relative
        sqllite = 'sqlite:///foo.db'
        connection_string = get_db_connection_string(sqllite)
        self.assertEqual(connection_string, 'sqlite:///foo.db')

        # absolute
        sqllite = 'sqlite:////foo.db'
        connection_string = get_db_connection_string(sqllite)
        self.assertEqual(connection_string, 'sqlite:////foo.db')


class TestDBConnector(unittest.TestCase):
    def setUp(self):
        if os.environ.get('TRAVIS') is None:
            self.db = DBConnector()

    def test_add_and_delete_data(self):
        if os.environ.get('TRAVIS') is None:
            github_data_import = GitHubData(
                                    date_updated=datetime.datetime.now(),
                                    language='repo_name',
                                    pull_requests=0,
                                    open_issues=0,
                                    number_of_commits=0,
                                    number_of_branches=0,
                                    number_of_releases=0,
                                    number_of_contributors=0,
                                    number_of_watchers=0,
                                    number_of_stargazers=0,
                                    number_of_forks=0
                                    )
            res = self.db.add_data(github_data_import)
            self.assertTrue(isinstance(res, GitHubData))
            res = self.db.delete_data(res.id, 'github_data')
            self.assertTrue(res)

            packagedata = PackageManagerData(
                                    date_updated=datetime.datetime.now(),
                                    csharp_downloads=0,
                                    nodejs_downloads=0,
                                    php_downloads=0,
                                    python_downloads=0,
                                    ruby_downloads=0
                                    )
            res = self.db.add_data(packagedata)
            self.assertTrue(isinstance(res, PackageManagerData))
            res = self.db.delete_data(res.id, 'package_manager_data')
            self.assertTrue(res)

    def test_get_data(self):
        if os.environ.get('TRAVIS') is None:
            github_data = self.db.get_data(GitHubData)
            self.assertTrue(isinstance(github_data, list))
            self.assertTrue(isinstance(github_data[0], GitHubData))


class TestGitHub(unittest.TestCase):
    def setUp(self):
        if os.environ.get('TRAVIS') is None:
            self.github = GitHub()
            self.db = DBConnector()
            self.config = Config()

    def test_update_library_data(self):
        if os.environ.get('TRAVIS') is None:
            res = self.github.update_library_data(self.config.github_user,
                                                  self.config.github_repos[0])
            self.assertTrue(isinstance(res, GitHubData))
            res = self.db.delete_data(res.id, 'github_data')
            self.assertTrue(res)


class TestPackageManagers(unittest.TestCase):
    def setUp(self):
        if os.environ.get('TRAVIS') is None:
            self.pm = PackageManagers()
            self.db = DBConnector()
            self.config = Config()

    def test_update_package_manager_data(self):
        if os.environ.get('TRAVIS') is None:
            res = self.pm.update_package_manager_data(
                self.config.package_manager_urls)
            self.assertTrue(isinstance(res, PackageManagerData))
            res = self.db.delete_data(res.id, 'package_manager_data')
            self.assertTrue(res)


class TestSendGridEmail(unittest.TestCase):
    def setUp(self):
        if os.environ.get('TRAVIS') is None:
            self.sg = SendGrid()
            self.config = Config()

    def test_send_email(self):
        if os.environ.get('TRAVIS') is None:
            res = self.sg.send_email(
                'elmer.thomas+test@sendgrid.com',
                self.config.from_email,
                self.config.email_subject,
                self.config.email_body
                )
            self.assertEqual(202, res[0])


class TestExportTable(unittest.TestCase):

    # Corresponds to schema in `db/data_schema.sql`
    header_row = "id,date_updated,language,pull_requests,open_issues,"\
                 "number_of_commits,number_of_branches,number_of_releases,"\
                 "number_of_contributors,number_of_watchers,"\
                 "number_of_stargazers,number_of_forks\n"

    def setUp(self):
        if os.environ.get('TRAVIS') is None:
            self.github = GitHub()
            self.db = DBConnector()
            self.config = Config()
            self.github.update_library_data(self.config.github_user,
                                            self.config.github_repos[0])
            self.filename = "./csv/{}.csv".format(GitHubData.__tablename__)

    def test_file_export_succeeds(self):
        if os.environ.get('TRAVIS') is None:
            self.assertFalse(os.path.exists(self.filename))
            self.db.export_table_to_csv(GitHubData)
            self.assertTrue(os.path.exists(self.filename))

    def test_file_export_has_correct_data(self):
        if os.environ.get('TRAVIS') is None:
            self.db.export_table_to_csv(GitHubData)
            with open(self.filename, 'r') as fp:
                exported_data = fp.readlines()

            # Table has correct header
            self.assertEqual(exported_data[0], self.header_row)

            # Table exported correct number of rows
            num_exported_rows = len(exported_data) - 1  # exclude header
            num_db_rows = len(self.db.get_data(GitHubData))
            self.assertEqual(num_exported_rows, num_db_rows)

    def tearDown(self):
        if os.environ.get('TRAVIS') is None:
            os.remove(self.filename)


class TestLicenseYear(unittest.TestCase):
    def setUp(self):
        self.license_file = 'LICENSE.txt'

    def test_license_year(self):
        copyright_line = ''
        with open(self.license_file, 'r') as f:
            for line in f:
                if line.startswith('Copyright'):
                    copyright_line = line.strip()
                    break
        self.assertEqual('Copyright (c) 2016-%s SendGrid, Inc.' %
                         datetime.datetime.now().year, copyright_line)


if __name__ == '__main__':
    unittest.main()
