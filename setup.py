from setuptools import setup

setup(
    name='spamfilter',
    version='0.1',
    py_modules=['spamfilter', "spammodel", "spamclassifier", "spam_config"],
    include_package_data=True,
    install_requires=[
        'click',
        # Colorama is only required for Windows.
        #'colorama',
    ],
    entry_points='''
        [console_scripts]
        spamfilter=spamfilter:cli
    ''',
)
