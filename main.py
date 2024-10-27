import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from functions.functions import *
import json
import mcrcon

def send(vk, message, id, message_id):
    vk.messages.send(
        user_id=id,
        message=message,
        random_id=0,
        reply_to=message_id
    )

config = json.load(open('config.json'))

token = config['token']

check_empty_users()

host = config["host"]
port = config["port"]
password = config["password"]

def main():
    vk_session = vk_api.VkApi(token=token)
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            message_text = event.text.strip()
            mid = event.message_id

            if message_text[0] == "!":
                command = message_text[1:]
                list_cmd = command.split()
                us = list_cmd[1] if len(list_cmd) > 1 else ""
                if us.startswith("[") and "|" in us:
                    us = us.split("|")[1].lstrip("@")[:-1]
                if list_cmd[0] == 'register':
                    if len(list_cmd) < 3:
                        vk.messages.send(
                            user_id=event.user_id,
                            message="❗️Использование: !register <username> <group>",
                            random_id=0,
                            reply_to=mid
                        )
                    else:
                        try:
                            id = vk.users.get(user_ids=us)[0]['id']
                            group = list_cmd[2]

                            data = check_user_in_db(event.user_id)[1]
                            groups = json.load(open('groups.json'))
                            data_weight = groups[data]["weight"] if data != "super" else 10 ** 5
                            groups_list = list(groups.keys())
                            if data not in groups_list and data != "super":
                                vk.messages.send(
                                    user_id=event.user_id,
                                    message='❌ Не удалось получить вашу группу.',
                                    random_id=0,
                                    reply_to=mid
                                )

                            elif id == int(event.user_id):
                                send(vk, "❌ Вы не можете использовать это на себе!", event.user_id, mid)

                            elif data == "super" or list_cmd[0] in groups[data]['allowed_super_commands']:
                                if check_user_in_db(id):
                                    send(vk, "⚠️ Этот пользователь уже зарегистрирован.", event.user_id, mid)
                                elif group not in groups_list:
                                    send(vk, "❌ Такой группы не существует!", event.user_id, mid)
                                elif data_weight <= groups[group]["weight"] or group == "super":
                                    send(vk, "⚠️ Вы не можете зарегистрировать пользователя с этой группой!", event.user_id, mid)
                                else:
                                    register(id, group)
                                    send(vk, f'✅ Вы зарегистрировали пользователя VK-{id} [{us}] с группой {group.upper()}!', event.user_id, mid)
                            else:
                                send(vk, "⚠️ Эта команда Вам не разрешена.", event.user_id, mid)
                        except IndexError:
                            send(vk, "❌ Пользователя с таким VK-username не существует!", event.user_id, mid)
                elif list_cmd[0] in ['unregister', 'remove']:
                    if len(list_cmd) < 2:
                        vk.messages.send(
                            user_id=event.user_id,
                            message=f"❗️Использование: !{list_cmd[0]} <username>",
                            random_id=0,
                            reply_to=mid
                        )
                    else:
                        try:
                            id = vk.users.get(user_ids=us)[0]['id']

                            data = check_user_in_db(event.user_id)[1]
                            data2 = check_user_in_db(id)[1]
                            groups = json.load(open('groups.json'))
                            groups_list = list(groups.keys())
                            data_weight = groups[data]["weight"] if data != "super" else 10**5
                            data_weight2 = groups[data2]["weight"] if data2 in groups_list else 0

                            if data not in groups_list and data != "super":
                                send(vk, "❌ Не удалось получить вашу группу.", event.user_id, mid)
                            elif id == event.user_id:
                                send(vk, "❌ Вы не можете использовать это на себе!", event.user_id, mid)
                            elif data == "super" or list_cmd[0] in groups[data]["allowed_super_commands"]:
                                if not check_user_in_db(id):
                                    send(vk, "⚠️ Этот пользователь не зарегистрирован.", event.user_id, mid)
                                elif data2 == "super" or data_weight <= data_weight2:
                                    send(vk, "⚠️ Вы не можете удалить этого пользователя!", event.user_id, mid)
                                else:
                                    unregister(id)
                                    send(vk, f"✅ Вы удалили пользователя VK-{id} [{us}]!", event.user_id, mid)
                            else:
                                send(vk, "⚠️ Эта команда Вам не разрешена.", event.user_id, mid)
                        except IndexError:
                            send(vk, "❌ Пользователя с таким VK-username не существует!", event.user_id, mid)
                elif list_cmd[0] == "group":
                    if len(list_cmd) < 2:
                        vk.messages.send(
                            user_id=event.user_id,
                            message=f"❗️Использование: !{list_cmd[0]} <username>",
                            random_id=0,
                            reply_to=mid
                        )
                    else:
                        try:
                            id = vk.users.get(user_ids=us)[0]['id']
                            group = list_cmd[2]

                            data = check_user_in_db(event.user_id)[1]
                            data2 = check_user_in_db(id)[1]
                            groups = json.load(open('groups.json'))
                            groups_list = list(groups.keys())
                            data_weight = groups[data]["weight"] if data != "super" else 10 ** 5

                            if data not in groups_list and data != "super":
                                send(vk, "❌ Не удалось получить вашу группу.", event.user_id, mid)
                            elif id == event.user_id:
                                send(vk, "❌ Вы не можете использовать это на себе!", event.user_id, mid)
                            elif data == "super" or list_cmd[0] in groups[data]["allowed_super_commands"]:
                                if not check_user_in_db(id):
                                    send(vk, "⚠️ Этот пользователь не зарегистрирован.", event.user_id, mid)
                                elif group not in groups_list:
                                    send(vk, "❌ Такой группы не существует!", event.user_id, mid)
                                elif data2 == "super" or groups[group]["weight"] >= data_weight:
                                    send(vk, "⚠️ Вы не можете установить пользователю эту группу!", event.user_id, mid)
                                else:
                                    set_group(id, group)
                                    send(vk, f"✅ Вы установили пользователю VK-{id} [{us}] группу {group.upper()}!", event.user_id, mid)
                            else:
                                send(vk, "⚠️ Эта команда Вам не разрешена.", event.user_id, mid)
                        except IndexError:
                            send(vk, "❌ Пользователя с таким VK-username не существует!", event.user_id, mid)
                elif list_cmd[0] == 'profile':
                    if check_user_in_db(event.user_id):
                        msg = "🔥 Ваш профиль\n"
                        msg += f"Группа: {check_user_in_db(event.user_id)[1]}\n\n"
                        msg += "Доступные команды:\n"

                        group = check_user_in_db(event.user_id)[1]

                        if group != "super":
                            groups = json.load(open("groups.json"))
                            allowed_commands = groups[group]["allowed_commands"]
                        else:
                            allowed_commands = ['*']
                        for i in allowed_commands:
                            msg += f"— {i}\n"

                        send(vk, msg, event.user_id, mid)
                else:
                    send(vk, "⚠️ Неизвестная команда!", event.user_id, mid)
            elif message_text.split()[0] == 'r':

                id = event.user_id
                data = check_user_in_db(id)

                if not data:
                    send(vk, "❌ Вам нельзя использовать эти команды!", id, mid)
                else:
                    try:
                        with mcrcon.MCRcon(host, password, port) as mcr:
                            command = message_text[2:]

                            if is_command_allowed(command, id) == Exception:
                                send(vk, "❌ Не удалось получить вашу группу.", id, mid)
                            elif not is_command_allowed(command, id):
                                send(vk, "⚠️ Эта команда Вам не разрешена.", id, mid)
                            else:
                                response = mcr.command(command)
                                formatted_resp = remove_minecraft_color_codes(response).strip('\n')
                                vk.messages.send(
                                    user_id=event.user_id,
                                    message=f"✉️ Ответ от сервера:\n\n{formatted_resp}",
                                    random_id=0,
                                    reply_to=mid
                                )
                    except Exception as e:
                        print(e)
                        vk.message.send(
                            user_id=event.user_id,
                            message="⚠️ Rcon недоступен!",
                            random_id=0,
                            reply_to=mid
                        )
            else:
                send(vk, "⚠️ Неизвестная команда!", event.user_id, mid)



if __name__ == '__main__':
    main()