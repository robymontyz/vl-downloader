"""
    PoliTO VL Downloader modules

    Modules to download video-lessons from "Portale della didattica"
    of Politecnico di Torino.

    :copyright: (c) 2016, robymontyz
    :license: BSD

    Permission to use, copy, modify, and distribute this software for any
    purpose with or without fee is hereby granted, provided that the above
    copyright notice and this permission notice appear in all copies.

    THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
    WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
    MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
    ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
    WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
    ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
    OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
"""


import requests
import os.path


from bs4 import BeautifulSoup


def login(_username, _password):
    """
    Login using Shibbolet.

    :return: session object, correctly logged in (None if usr or psw are not correct).
    """

    s = requests.session()

    login_data = {
        'j_username': _username,
        'j_password': _password
    }

    s.get('https://login.didattica.polito.it/secure/ShibLogin.php')  # set cookies
    r = s.post('https://idp.polito.it/idp/Authn/X509Mixed/UserPasswordLogin', login_data)

    soup = BeautifulSoup(r.content, 'lxml')

    # check if login attributes are correct (searching for a specific span)
    tag = soup.find('span', id="loginerror")
    if tag is not None and tag.string == 'Errore al login. Verifica username e password':
        return None
    else:
        # if correct:
        tag = soup.find_all('input')
        relay_state_value = tag[0]['value']
        saml_response_value = tag[1]['value']
        data = {
            'RelayState': relay_state_value,
            'SAMLResponse': saml_response_value
        }
        s.post('https://login.didattica.polito.it/Shibboleth.sso/SAML2/POST', data)

        return s


def get_video_urls(s, _course_link):
    """
    Get all the video-lessons URLs starting from the URL of any lesson
    (first one is better).

    :param s: session object
    :param _course_link: URL of the lesson to start with
    :return: a list with all the video-lessons URLs
    """

    urls = []
    lessons_list = []

    # get relative path to every lessons scraping the HTML
    page = s.get(_course_link)
    soup = BeautifulSoup(page.content, 'lxml')
    for link in soup.find('ul', id="navbar_left_menu").find_all('li', id=""):
        for a in link.find_all("a"):
            lessons_list.append(a.get('href'))

    # get all the direct links to the videos (.mp4)
    for lesson in lessons_list:
        page = s.get('https://didattica.polito.it/portal/pls/portal/' + lesson)
        soup = BeautifulSoup(page.content, 'lxml')
        video_url = soup.find('source')['src']
        urls.append(video_url)

    return urls


def download_video(s, url, _dir):
    """
    Download a video using the direct link

    :param s: session object
    :param url: direct link to a single video
    :param _dir: download location
    """

    r = s.get(url, stream=True)
    filename = url.split('/')[-1].split('#')[0].split('?')[0]

    with open(os.path.join(_dir, filename), 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            f.write(chunk)

    return None


if __name__ == "__main__":
    # use for testing

    username = 'S012345'
    password = 'password'
    course_link = 'https://didattica.polito.it/portal/pls/portal/sviluppo.videolezioni.vis?cor=191&lez=8083'
    dl_path = '/Users/foo/Downloads/CE/'

    # session = login(username, password)
    #
    # urls = get_video_urls(session, course_link)
    #
    # for url in urls:
    #     print url
    #     # download_video(session, url, dl_path)
