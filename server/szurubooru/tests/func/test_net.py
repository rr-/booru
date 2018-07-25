from szurubooru.func import net


def test_download(config_injector):
    config_injector({
        'user_agent': None
    })
    url = 'http://info.cern.ch/hypertext/WWW/TheProject.html'

    expected_content = (
        b'<HEADER>\n<TITLE>The World Wide Web project</TITLE>\n<NEXTID N="' +
        b'55">\n</HEADER>\n<BODY>\n<H1>World Wide Web</H1>The WorldWideWeb' +
        b' (W3) is a wide-area<A\nNAME=0 HREF="WhatIs.html">\nhypermedia</' +
        b'A> information retrieval\ninitiative aiming to give universal\na' +
        b'ccess to a large universe of documents.<P>\nEverything there is ' +
        b'online about\nW3 is linked directly or indirectly\nto this docum' +
        b'ent, including an <A\nNAME=24 HREF="Summary.html">executive\nsum' +
        b'mary</A> of the project, <A\nNAME=29 HREF="Administration/Mailin' +
        b'g/Overview.html">Mailing lists</A>\n, <A\nNAME=30 HREF="Policy.h' +
        b'tml">Policy</A> , November\'s  <A\nNAME=34 HREF="News/9211.html"' +
        b'>W3  news</A> ,\n<A\nNAME=41 HREF="FAQ/List.html">Frequently Ask' +
        b'ed Questions</A> .\n<DL>\n<DT><A\nNAME=44 HREF="../DataSources/T' +
        b'op.html">What\'s out there?</A>\n<DD> Pointers to the\nworld\'s ' +
        b'online information,<A\nNAME=45 HREF="../DataSources/bySubject/Ov' +
        b'erview.html"> subjects</A>\n, <A\nNAME=z54 HREF="../DataSources/' +
        b'WWW/Servers.html">W3 servers</A>, etc.\n<DT><A\nNAME=46 HREF="He' +
        b'lp.html">Help</A>\n<DD> on the browser you are using\n<DT><A\nNA' +
        b'ME=13 HREF="Status.html">Software Products</A>\n<DD> A list of W' +
        b'3 project\ncomponents and their current state.\n(e.g. <A\nNAME=2' +
        b'7 HREF="LineMode/Browser.html">Line Mode</A> ,X11 <A\nNAME=35 HR' +
        b'EF="Status.html#35">Viola</A> ,  <A\nNAME=26 HREF="NeXT/WorldWid' +
        b'eWeb.html">NeXTStep</A>\n, <A\nNAME=25 HREF="Daemon/Overview.htm' +
        b'l">Servers</A> , <A\nNAME=51 HREF="Tools/Overview.html">Tools</A' +
        b'> ,<A\nNAME=53 HREF="MailRobot/Overview.html"> Mail robot</A> ,<' +
        b'A\nNAME=52 HREF="Status.html#57">\nLibrary</A> )\n<DT><A\nNAME=4' +
        b'7 HREF="Technical.html">Technical</A>\n<DD> Details of protocols' +
        b', formats,\nprogram internals etc\n<DT><A\nNAME=40 HREF="Bibliog' +
        b'raphy.html">Bibliography</A>\n<DD> Paper documentation\non  W3 a' +
        b'nd references.\n<DT><A\nNAME=14 HREF="People.html">People</A>\n<' +
        b'DD> A list of some people involved\nin the project.\n<DT><A\nNAM' +
        b'E=15 HREF="History.html">History</A>\n<DD> A summary of the hist' +
        b'ory\nof the project.\n<DT><A\nNAME=37 HREF="Helping.html">How ca' +
        b'n I help</A> ?\n<DD> If you would like\nto support the web..\n<D' +
        b'T><A\nNAME=48 HREF="../README.html">Getting code</A>\n<DD> Getti' +
        b'ng the code by<A\nNAME=49 HREF="LineMode/Defaults/Distribution.h' +
        b'tml">\nanonymous FTP</A> , etc.</A>\n</DL>\n</BODY>\n')

    actual_content = net.download(url)
    assert actual_content == expected_content
