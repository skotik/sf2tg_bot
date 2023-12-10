#!/usr/bin/python
import json
import socket
from time import sleep
# import pprint
import six
import my
from six.moves.urllib.request import Request as url_request
from six.moves.urllib.request import urlopen as url_open
from six.moves.urllib.parse import urlencode as url_encode
from six.moves.urllib.error import HTTPError as HTTPError

group_id = my.group_id
tg_id = my.tg_id
bot_token = my.bot_token
bot_api = 'https://api.telegram.org/bot'
bot_url = bot_api+bot_token


def encode_multipart_formdata(fields, files):
    LIMIT = b'----------lImIt_of_THE_fIle_eW_$'
#    CRLF = '\r\n'
    body = b''
    for key, value in fields.items():
        body = body+b'\r\n'+b'--' + LIMIT
        body = body+b'\r\n'+b'Content-Disposition: form-data; name="%s"' % six.ensure_binary(key)
        body = body+b'\r\n'+b''
        body = body+b'\r\n'+six.ensure_binary(value)
    for (key, filename, ftype, value) in files:
        body = body+b'\r\n'+b'--' + LIMIT
        body = body+b'\r\n'+b'Content-Disposition: form-data; name="%s"; filename="%s"' % (six.ensure_binary(key), six.ensure_binary(six.ensure_str(filename)))
        body = body+b'\r\n'+b'Content-Type: %s' % six.ensure_binary(ftype)
        body = body+b'\r\n'+b''
        body = body+b'\r\n'+six.ensure_binary(value)
    body = body+b'\r\n'+b'--' + LIMIT + b'--'
    body = body+b'\r\n'+b''
#    body = CRLF.join(L)
    content_type = b'multipart/form-data; boundary=%s' % LIMIT
    return content_type, body


def getUrlFileSize(url):
    request = url_request(url)
    request.get_method = lambda: 'HEAD'
    response = url_open(request)
#   print(response.info())
    return int(response.info().get('Content-Length', 10*1024*1024*1024)), response.info().get('Content-Type', 'application/octet-stream')


def ParseMessages(m, p_text='', is_fwd=False):
    for c_m in m:
        if (is_fwd or c_m.get('peer_id',False) in group_id ):
            vkUser = next(item for item in vkLongPollHistory['response']['profiles'] if item["id"] == c_m['from_id'])
            sVkUser = "<b>"+vkUser['first_name']+" "+vkUser['last_name']+"</b>\n"
            if (c_m.get('fwd_messages')):
                ParseMessages(c_m['fwd_messages'], sVkUser+c_m['text'], True)
            else:
                if (c_m['attachments']):
                    try:
                        for c_a in c_m['attachments']:
                            if (c_a['type'] == 'photo'):
                                max_h = 0
                                max_url = ''
                                for c_size in c_a['photo']['sizes']:
                                    if (c_size['height'] >= max_h):
                                        max_h = c_size['height']
                                        max_url = c_size['url']
                                data = {'photo': max_url, 'chat_id': tg_id, 'parse_mode': 'HTML', 'caption': six.ensure_str(sVkUser + '' + c_m['text'] + ("\nfwd: " + p_text if p_text else ''))}
                                url_open(bot_url+"/sendPhoto", six.ensure_binary(url_encode(data)))
                            if (c_a['type'] == 'video'):
                                data = {'chat_id': tg_id, 'parse_mode': 'HTML', 'text': six.ensure_str(sVkUser+'' + c_m['text'] + ("\nfwd: " + p_text if p_text else '') + "\n<a href='" + c_a['video']['player'] + "'>Video</a>")}
                                url_open(bot_url+"/sendMessage", six.ensure_binary(url_encode(data)))
                            if (c_a['type'] == 'doc'):
                                (doc_size, doc_type) = getUrlFileSize(c_a['doc']['url'])
                                print("\nfs: " + str(doc_size) + ' ft: '+doc_type)
                                if (doc_size < 10*1024*1024):
                                    docdata = url_open(c_a['doc']['url'])
                                    data = {'chat_id': tg_id, 'parse_mode': 'HTML', 'caption': six.ensure_str(sVkUser + '' + c_m['text'] + ("\nfwd: " + p_text if p_text else '') + "\n" + c_a['doc']['title'])}
                                    (h_ctype, f_data) = encode_multipart_formdata(data, [['document', c_a['doc']['title'], doc_type, docdata.read()]])
                                    url_open(url_request(bot_url+"/sendDocument", f_data, {'Content-Type': h_ctype}))
                                else:
                                    data = {'chat_id': tg_id, 'parse_mode': 'HTML', 'text': six.ensure_str(sVkUser + '' + c_m['text'] + ("\nfwd: " + p_text if p_text else '') + "\n<a href='"+c_a['doc']['url'] + "'>Document</a> " + c_a['doc']['title'])}
                                    url_open(bot_url+"/sendMessage", six.ensure_binary(url_encode(data)))
                    except HTTPError as e:
                        pass
                        print("\n" + e.fp.read())
                        exit()
                else:
                    if(c_m.get('action',False)): continue
                    data = {'chat_id': tg_id, 'parse_mode': 'HTML', 'text': six.ensure_str(sVkUser + '' + c_m['text'] + ('fwd: ' + p_text if p_text else ''))}
                    url_open(bot_url+"/sendMessage", six.ensure_binary(url_encode(data)))


def getMessage(cmid, peer_id):
    data = {"access_token": access_token, "v": '5.199', 'conversation_message_ids': cmid, 'peer_id': peer_id, 'group_id': 0, 'extended': 1}
    req = url_request(url="https://api.vk.com/method/messages.getByConversationMessageId", headers=headers, data=six.ensure_binary(url_encode(data)))
    vkMessage = json.loads(url_open(req).read())
    print(vkMessage)
#    [4, 46, 3, -205879084, 1701049143, u'test3', {u'title': u' ... '}]
#    data = { "access_token": access_token,"v": '5.199', 'message_ids':id , 'peer_id':'-205879084', 'group_id':0}
#    req = urllib2.request(url="https://api.vk.com/method/messages.getById",headers=headers,data=urllib.urlencode(data))


headers = my.headers
cookie = my.cookie
cookie.update(headers)


def getAccessToken():
    req = url_request(url="https://web.vk.me/?act=web_token&app_id=8202606", headers=cookie)
    f = url_open(req)
    vkWebToken = json.loads(f.read())
    return vkWebToken[1]['access_token']


def getLongPollServer():
    data = {"need_pts": '1', "access_token": access_token, "v": '5.199'}
    req = url_request(url="https://api.vk.com/method/messages.getLongPollServer", headers=headers, data=six.ensure_binary(url_encode(data)))
    return json.loads(url_open(req).read())


access_token = getAccessToken()
vkLongPollServer = getLongPollServer()
vkLastTs = vkLongPollServer['response']['ts']
vkLastPts = vkLongPollServer['response']['pts']
print("Pool start\n")
while True:
    try:
        data = {'act': 'a_check', 'wait': 25, 'mode': 34, 'version': 19, 'key': vkLongPollServer['response']['key'], 'ts': vkLongPollServer['response']['ts']}
        req = url_request(url="https://"+vkLongPollServer['response']['server'], headers=headers, data=six.ensure_binary(url_encode(data)))
        vkEvent = json.loads(url_open(req, timeout=30).read())
        six.print_(vkEvent, end="\r")
        if not vkEvent.get('ts', False):
            vkEvent['ts'] = vkLastTs
        elif vkLastTs != vkEvent['ts']:
            print()
        if ((vkEvent.get('failed', False) == 2) or (vkEvent.get('error') and vkEvent['error'].get('error_code') == 5)):
            access_token = getAccessToken()
            vkLongPollServer = getLongPollServer()
        elif (vkEvent.get('error')):
            pass
        else:
            vkLongPollServer['response']['ts'] = vkEvent['ts']
        if vkEvent.get('updates'):
            for vkUpdate in vkEvent['updates']:
                if (vkUpdate[0] == 10004 and vkUpdate[4] in group_id):
                    data = {"extended": 1, "pts": vkLastPts, "fields": "id,first_name,last_name", "access_token": access_token, "v": '5.199'}
                    req = url_request(url="https://api.vk.com/method/messages.getLongPollHistory", data=six.ensure_binary(url_encode(data)))
                    vkLongPollHistory = json.loads(url_open(req).read())
                    if ((vkLongPollHistory.get('failed', False) == 2) or (vkLongPollHistory.get('error') and vkLongPollHistory['error'].get('error_code') == 5)):
                        access_token = getAccessToken()
                        data = {"extended": 1, "pts": vkLastPts, "fields": "id,first_name,last_name", "access_token": access_token, "v": '5.199'}
                        req = url_request(url="https://api.vk.com/method/messages.getLongPollHistory", data=six.ensure_binary(url_encode(data)))
                        vkLongPollHistory = json.loads(url_open(req).read())

                    if not vkLongPollHistory.get('response', False):
                        print("")
                        print(vkLongPollHistory)
                    else:
                        ParseMessages(vkLongPollHistory['response']['messages']['items'])
                        vkLastTs = vkEvent['ts']
#                    pprint.pprint(vkLongPollHistory)
                    break
            vkLastPts=vkEvent['pts']
        vkLastTs = vkEvent['ts']
    except KeyboardInterrupt:
        exit()
        pass
    except socket.timeout:
        print("\nSocket timeout! sleep 1 minute")
        sleep(60)
# req["response"]["messages"]["items"], req["response"]["profiles"]
# updates [[10004, 10, 3, 50, -205879084, 1701052252, u'x', {u'title': u' ... '}, {}, 50, 0]]]
# {u'ts': 1811110834, u'updates': []}
