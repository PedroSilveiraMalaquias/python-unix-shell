import os
import subprocess


def handle_command(command, to_pipe=False, prev_output=None):
    output = None
    background = None
    input_file_name = None
    output_file_name = None

    if '|' in command:
        # Dividir o comando em duas partes: comando à esquerda e comando à direita do pipe
        left_command, right_command = command.split('|', 1)

        # Executar o comando à esquerda e redirecionar sua saída para a entrada do segundo comando:
        output1 = handle_command(left_command, True)
        return handle_command(right_command, False, output1)

    if '&' in command:
        background = True
        command = command.replace('&', '')
    # Verifica se há redirecionamento de saída
    if '>' in command:
        output_file_name = command.split('>')[1].strip()
        command = command.split('>')[0].strip()
    # Verifica se há redirecionamento de entrada
    if '<' in command:
        input_file_name = command.split('<')[1].strip()
        command = command.split('<')[0].strip()

    # Divide o comando em uma lista de palavras
    words = command.split()

    if prev_output is not None:
        words.append(prev_output)

    file_input = None
    file_output = None

    if input_file_name is not None:
        file_input = open(input_file_name, 'r')

    if output_file_name is not None:
        file_output = open(output_file_name, 'w')

    # Verifica se o comando é "cd"
    if words[0] == 'cd':
        # Verifica se o diretório existe
        if os.path.exists(words[1]):
            # Muda o diretório atual para o diretório especificado pelo usuário
            if file_input is None:
                os.chdir(words[1])
            else:
                subprocess.run(words, check=True, stdin=file_input)
        else:
            # Exibe uma mensagem de erro, caso o diretório não exista
            output = f"O diretório '{words[1]}' não existe."
    # Verifica se o comando é "pwd"
    elif words[0] == 'pwd':
        # Imprime o diretório atual
        if file_output is None:
            output = os.getcwd()
        else:
            subprocess.run(words, check=True, stdout=file_output)
    # Verifica se o comando é "exit"
    elif words[0] == 'exit':
        # Sai do shell
        exit()
    # Verifica se o comando é "cp"
    elif words[0] == 'cp':
        # Copia o arquivo especificado pelo usuário para o diretório de destino
        if background:
            if file_input is None:
                subprocess.Popen(words[:3])
            else:
                subprocess.Popen(words[:1], stdin=file_input)
        else:
            if file_input is None:
                subprocess.run(words, check=True)
            else:
                subprocess.run(words, check=True, stdin=file_input)
    # Verifica se o comando é "mv"
    elif words[0] == 'mv':
        # Renomeia o arquivo especificado pelo usuário para o novo nome
        if background:
            if file_input is None:
                subprocess.Popen(words)
            else:
                subprocess.Popen(words, stdin=file_input)
        else:
            if file_input is None:
                subprocess.run(words)
            else:
                subprocess.run(words, stdin=file_input)
    # Verifica se o comando é "rm"
    elif words[0] == 'rm':
        # Remove o arquivo especificado pelo usuário
        try:
            if file_input is None:
                os.remove(words[1])
            else:
                os.remove(file_input.read())
        except IndexError:
            print('rm: argumento ausente')
        except FileNotFoundError:
            print(f'{words[1]}: arquivo não encontrado')
    # Verifica se o comando é "ls"
    elif words[0] == 'ls':
        # Lista o conteúdo do diretório atual
        if background:
            if file_output is None:
                output = subprocess.check_output(words[0])
                output = output.decode()
            else:
                subprocess.Popen(words, stdout=file_output)
        else:
            if file_output is None:
                output = subprocess.run(words, capture_output=True)
                output = output.stdout.decode()
            else:
                subprocess.run(words, check=True, stdout=file_output)
    # Verifica se o comando é "cat"
    elif words[0] == 'cat':
        # Imprime o conteúdo do arquivo especificado pelo usuário

        file_name = words[1] if file_input is None else file_input.read()
        try:
            with open(file_name, 'r') as f:
                if file_output is None:
                    output = f.read()
                else:
                    file_output.write(f.read())
        except IndexError:
            output = 'rm: argumento ausente'
        except FileNotFoundError:
            output = f'{file_name}: arquivo não encontrado'
    # Verifica se o comando é "echo"
    elif words[0] == 'echo':
        # Imprime as palavras fornecidas pelo usuário
        text = ' '.join(words[1:]) if file_input is None else file_input.read()
        if file_output is None:
            output = text
        else:
            file_output.write(text)
    elif words[0] == 'mkdir':
        # Cria o diretório especificado pelo usuário

        dir_name = words[1] if file_input is None else file_input.read()
        try:
            os.mkdir(dir_name)
        except IndexError:
            output = 'mkdir: argumento ausente'
        except FileExistsError:
            output = f"{dir_name}: diretório já existe"
    elif words[0] == 'rmdir':
        dir_name = words[1] if file_input is None else file_input.read()
        try:
            if os.path.exists(dir_name):
                os.rmdir(dir_name)
            else:
                output = f'{dir_name}: diretório não encontrado'
        except IndexError:
            output = 'rmdir: argumento ausente'
        except OSError:
            output = f'{dir_name}: diretório não vazio'
    elif words[0] == 'touch':
        # Cria o arquivo especificado pelo usuário
        file_name = words[1] if file_input is None else file_input.read()
        try:
            open(file_name, 'a').close()
        except IndexError:
            output = 'touch: argumento ausente'
        except FileExistsError:
            output = f'{file_name}: arquivo já existe'
    else:
        # Se o comando não for reconhecido, imprime uma mensagem de erro
        output = f"Comando desconhecido: {words[0]}"

    if file_input is not None:
        file_input.close()

    if file_output is not None:
        file_output.close()

    if not to_pipe:
        if output:
            print(output)
    else:
        return output


# Loop principal do shell
while True:
    # Mostra o prompt do shell
    prompt = f"{os.getcwd()} $ "
    # Pede ao usuário para inserir um comando
    command = input(prompt)

    handle_command(command)
