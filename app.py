import paramiko
import tomli
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import os

def runScript(scriptFile, config='./config.toml', arguments=[]):    
    if not os.path.exists(config): 
        print(f'The config file ({config}) does not exist')
        return f'The config file ({config}) does not exist'
    if not os.path.exists(scriptFile): 
        print(f'The script file ({scriptFile}) does not exist')
        return f'The script file ({scriptFile}) does not exist'
    
    with open(config, 'rb') as configFile:
        try:
            config = tomli.load(configFile)
        except tomli.TOMLDecodeError as e:
            print(f'TOMLDecodeError: {e}')
            return f'TOMLDecodeError: {e}'
            
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname=config.get('host').get('ip'), username=config.get('host').get('username'), password=config.get('host').get('password'))
    except Exception as e:
        print(e)
        return e
    
    try:
        sftp = client.open_sftp()
        remote_path = f'/home/{config.get("host").get("username")}/s'
        sftp.put(scriptFile, remote_path)
        sftp.close()
    except Exception as e:
        print(f'SFTP Error: {e}')
        client.close()
        return f'SFTP Error: {e}'
    
    commands = [
        f'chmod +x {remote_path}',
        remote_path + ' ' + ' '.join(arguments),
        f'rm {remote_path}'
    ]


    for command in commands:
        _, stdout, stderr = client.exec_command(command)
        if commands.index(command) == 1:
            outc = stdout.read().decode() + stderr.read().decode()
            out = outc
        
    client.close()
    return out
    
def overflowcanceler(texto, max_caracteres):
    if len(texto) > max_caracteres:
        return '...' + texto[(max_caracteres - 3):]# Acorta y añade '...'
    return texto  # Devuelve el texto original si no es necesario acortarlo

def set_placeholder(entry, placeholder):
    # Función para manejar el foco cuando el usuario ingresa al campo
    def on_focus_in(event):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)  # Eliminar el texto del placeholder
            entry.config(fg='white')  # Cambiar el color del texto a negro

    # Función para manejar el foco cuando el usuario sale del campo
    def on_focus_out(event):
        if entry.get() == '':  # Si el campo está vacío
            entry.insert(0, placeholder)  # Insertar el texto del placeholder
            entry.config(fg='gray')  # Cambiar el color del texto a gris

    # Insertar el placeholder inicialmente y configurar color
    entry.insert(0, placeholder)
    entry.config(fg='gray')

    # Enlazar los eventos de foco
    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)
    
def main():
    ventana = tk.Tk()
    ventana.title("Script Runner")
    ventana.geometry("900x500")
    ventana.configure(bg='black')
    ventana.iconbitmap('icon.ico')
    
    ventana.grid_rowconfigure([0, 1, 2, 3, 4, 5], weight=1)
    ventana.grid_columnconfigure([0, 1], weight=1)
    
    style = ttk.Style()
    style.configure('Vertical.TScrollbar',
                    background='#000',
                    troughcolor='#333',
                    arrowcolor='#333',
                    gripcount=0)
    style.configure('Horizontal.TScrollbar',
                    background='#000',
                    troughcolor='#333',
                    arrowcolor='#333',
                    gripcount=0)
    
    def selectFile(label, filetypes, message):
        archivo = filedialog.askopenfilename(
            title="Selecciona un archivo", 
            filetypes=filetypes
        )
        if archivo:
            label.config(text=f"{message}: {overflowcanceler(archivo, 40)}")
            return archivo
        
    def replacetext(text = str, text_widget = tk.Text):
        text_widget.config(state=tk.NORMAL)  # Habilita temporalmente la edición
        text_widget.delete("1.0", tk.END)  # Borra todo el texto en el widget
        text_widget.insert(tk.END, text)  # Inserta el nuevo texto
        text_widget.config(state=tk.DISABLED)  # Deshabilita la edición nuevamente
        # out_field.config(yscrollcommand=v_scrollbar.set, xscrollcommand=x_scrollbar.set)

    scriptFile = tk.StringVar()
    configFile = tk.StringVar()
    header = tk.Label(ventana, text='Script Runner', font=('Arial', 20), bg='black', fg='white')
    labelArchivoScript = tk.Label(ventana, text='Ningun script seleccionado ', font=('Arial', 13), bg='black', fg='white')
    botonArchivoScript = tk.Button(ventana, text='Selecionar archivo', font=('Arial', 13), command=lambda: scriptFile.set(selectFile(labelArchivoScript, [('El archivo de script', '*.*')], 'Script seleccionado')), relief='groove', bg='#333', fg='white')
    labelArchivoConfiguracion = tk.Label(ventana, text='Ningun archivo de configuracion seleccionado ', font=('Arial', 13), bg='black', fg='white')
    botonArchivoConfiguracion = tk.Button(ventana, text='Selecionar archivo', font=('Arial', 13), command=lambda: configFile.set(selectFile(labelArchivoConfiguracion, [('El archivo de configuracion', '*.toml')], 'Archivo de configuarcion seleccionado')), relief='groove', bg='#333', fg='white')
    args = tk.Entry(ventana, font=("Arial", 14), width=40, bg='#111', fg='white', insertbackground='white')
    out = tk.Frame(ventana, height=10, width=40)
    out.grid(row=5, column=0, columnspan=2)
    set_placeholder(args, 'Argumentos')
    out_field = tk.Text(out, height=10, width=40, font=("Arial", 12), wrap='none', bg='#111', fg='white', insertbackground='white')
    out_field.insert(tk.END, '')
    out_field.config(state='disabled')
    out_field.grid(column=0, row=0, sticky='nsew')
    v_scrollbar = ttk.Scrollbar(out, orient=tk.VERTICAL, command=out_field.yview, style='Vertical.TScrollbar')
    v_scrollbar.grid(column=1, row=0, sticky='ns')
    x_scrollbar = ttk.Scrollbar(out, orient=tk.HORIZONTAL, command=out_field.xview, style='Horizontal.TScrollbar')
    x_scrollbar.grid(column=0, row=1, columnspan=2, sticky='ew')
    out_field.config(yscrollcommand=v_scrollbar.set, xscrollcommand=x_scrollbar.set)
    args.grid(row=3, column=0, columnspan=2)
    ejecutarScriptBoton = tk.Button(ventana, text='Ejecutar script', font=('Arial', 13), command=lambda: replacetext(runScript(scriptFile.get(), configFile.get(), args.get().split()), out_field), relief='groove', bg='#333', fg='white')
    labelArchivoScript.grid(row=1, column=0)
    botonArchivoScript.grid(row=1, column=1)
    labelArchivoConfiguracion.grid(row=2, column=0)
    botonArchivoConfiguracion.grid(row=2, column=1)
    ejecutarScriptBoton.grid(row=4, column=0, columnspan=2)
    header.grid(row=0, column=0, columnspan=2)

    ventana.mainloop()
    
if __name__ == '__main__':
    main()