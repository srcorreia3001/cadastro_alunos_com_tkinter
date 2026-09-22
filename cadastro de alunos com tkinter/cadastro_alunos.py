import os
import sqlite3
from datetime import datetime
from tkinter import (
    END,
    Button,
    Entry,
    Frame,
    Label,
    Listbox,
    Scrollbar,
    StringVar,
    Tk,
    Toplevel,
    filedialog,
    messagebox,
    ttk,
)

# Tenta importar Pillow para renderizar imagens (JPEG, PNG, etc.)
try:
    from PIL import Image, ImageTk

    HAS_PIL = True
except ImportError:
    HAS_PIL = False

#Tentar importar o Pilow para rendenrizar imagens JPg,PNG e etc...

#======================================================
#BANCO DE DADOS
#======================================================

def conectar_bd():
    conn = sqlite3.connect("escola.db")
    cursor = conn.cursor()
    cursor.execute(
        """

        CREATE TABLE IF NOT EXISTS alunos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            data_nascimento TEXT,
            email TEXT,
            telefone TEXT,
            serie TEXT,
            nota1 REAL,
            nota2 REAL,
            media REAL,
            foto BLOB
        )
"""
    )
    conn.commit()
    conn.close()

#FUNÇOES 

def salvar_aluno(
    nome,
    data_nasc,
    email,
    telefone,
    serie,
    nota1,
    nota2,
    foto_bytes,
    aluno_id=None,
):
    try:
        n1 = float(nota1) if nota1 else 0.0
        n2 = float(nota2) if nota2 else 0.0
        media = round((n1 + n2) / 2, 2)
    except ValueError:
        raise ValueError("As notas devem ser números válidos.")

    conn = sqlite3.connect("escola.db")
    cursor = conn.cursor()

    if aluno_id:
        if foto_bytes is not None:
            cursor.execute(
                """
                UPDATE alunos SET nome=?, data_nascimento=?, email=?, telefone=?, serie=?, nota1=?, nota2=?, media=?, foto=?
                WHERE id=?
            """,
                (
                    nome,
                    data_nasc,
                    email,
                    telefone,
                    serie,
                    n1,
                    n2,
                    media,
                    foto_bytes,
                    aluno_id,
                ),
            )
        else:
            cursor.execute(
                """
                UPDATE alunos SET nome=?, data_nascimento=?, email=?, telefone=?, serie=?, nota1=?, nota2=?, media=?
                WHERE id=?
            """,
                (
                    nome,
                    data_nasc,
                    email,
                    telefone,
                    serie,
                    n1,
                    n2,
                    media,
                    aluno_id,
                ),
            )
    else:
        cursor.execute(
            """
            INSERT INTO alunos (nome, data_nascimento, email, telefone, serie, nota1, nota2, media, foto)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                nome,
                data_nasc,
                email,
                telefone,
                serie,
                n1,
                n2,
                media,
                foto_bytes,
            ),
        )

    conn.commit()
    conn.close()


def listar_alunos():
    conn = sqlite3.connect("escola.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, nome, serie, media FROM alunos ORDER BY nome ASC"
    )
    alunos = cursor.fetchall()
    conn.close()
    return alunos


def buscar_aluno_por_id(aluno_id):
    conn = sqlite3.connect("escola.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM alunos WHERE id=?", (aluno_id,))
    aluno = cursor.fetchone()
    conn.close()
    return aluno


def deletar_aluno(aluno_id):
    conn = sqlite3.connect("escola.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM alunos WHERE id=?", (aluno_id,))
    conn.commit()
    conn.close()


# ==========================================
# INTERFACE GRÁFICA (TKINTER)
# ==========================================
class AppCadastro:

    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Cadastro de Alunos")
        self.root.geometry("850x550")
        self.root.resizable(False, False)

        conectar_bd()

        self.foto_bytes = None
        self.aluno_selecionado_id = None

        self.setup_ui()
        self.atualizar_lista()

    def setup_ui(self):
        # Frame Esquerdo: Formulário (usando ttk.Frame)
        frame_form = ttk.Frame(self.root, padding=10)
        frame_form.place(x=10, y=10, width=480, height=530)

        Label(
            frame_form,
            text="Cadastro de Aluno",
            font=("Arial", 14, "bold"),
        ).grid(row=0, column=0, columnspan=2, pady=10)

        # Campos do Formulário
        Label(frame_form, text="Nome:").grid(
            row=1, column=0, sticky="w", pady=4
        )
        self.ent_nome = Entry(frame_form, width=35)
        self.ent_nome.grid(row=1, column=1, pady=4)

        Label(frame_form, text="Data Nasc. (DD/MM/AAAA):").grid(
            row=2, column=0, sticky="w", pady=4
        )
        self.ent_data_nasc = Entry(frame_form, width=35)
        self.ent_data_nasc.grid(row=2, column=1, pady=4)

        Label(frame_form, text="E-mail:").grid(
            row=3, column=0, sticky="w", pady=4
        )
        self.ent_email = Entry(frame_form, width=35)
        self.ent_email.grid(row=3, column=1, pady=4)

        Label(frame_form, text="Telefone:").grid(
            row=4, column=0, sticky="w", pady=4
        )
        self.ent_telefone = Entry(frame_form, width=35)
        self.ent_telefone.grid(row=4, column=1, pady=4)

        Label(frame_form, text="Série/Ano:").grid(
            row=5, column=0, sticky="w", pady=4
        )
        self.ent_serie = Entry(frame_form, width=35)
        self.ent_serie.grid(row=5, column=1, pady=4)

        Label(frame_form, text="Nota 1:").grid(
            row=6, column=0, sticky="w", pady=4
        )
        self.ent_nota1 = Entry(frame_form, width=35)
        self.ent_nota1.grid(row=6, column=1, pady=4)

        Label(frame_form, text="Nota 2:").grid(
            row=7, column=0, sticky="w", pady=4
        )
        self.ent_nota2 = Entry(frame_form, width=35)
        self.ent_nota2.grid(row=7, column=1, pady=4)

        # Secção da Foto
        Label(frame_form, text="Foto:").grid(
            row=8, column=0, sticky="nw", pady=4
        )
        frame_foto = Frame(frame_form)
        frame_foto.grid(row=8, column=1, sticky="w", pady=4)

        self.lbl_foto = Label(
            frame_foto,
            text="Sem Foto",
            bg="#e0e0e0",
            width=15,
            height=5,
            relief="groove",
        )
        self.lbl_foto.pack(side="left", padx=5)

        btn_carregar_foto = Button(
            frame_foto, text="Selecionar Foto", command=self.carregar_foto
        )
        btn_carregar_foto.pack(side="left", padx=5)

        # Botões de Ação
        frame_botoes = Frame(frame_form)
        frame_botoes.grid(row=9, column=0, columnspan=2, pady=20)

        Button(
            frame_botoes,
            text="Salvar",
            bg="#4CAF50",
            fg="white",
            width=10,
            command=self.salvar,
        ).pack(side="left", padx=5)
        Button(
            frame_botoes,
            text="Limpar",
            width=10,
            command=self.limpar_formulario,
        ).pack(side="left", padx=5)
        Button(
            frame_botoes,
            text="Excluir",
            bg="#f44336",
            fg="white",
            width=10,
            command=self.excluir,
        ).pack(side="left", padx=5)

        # Frame Direito: Tabela de Alunos (usando ttk.Frame)
        frame_tabela = ttk.Frame(self.root, padding=10)
        frame_tabela.place(x=500, y=10, width=340, height=530)

        Label(
            frame_tabela,
            text="Alunos Cadastrados",
            font=("Arial", 12, "bold"),
        ).pack(pady=5)

        colunas = ("id", "nome", "serie", "media")
        self.tree = ttk.Treeview(
            frame_tabela, columns=colunas, show="headings", height=20
        )

        self.tree.heading("id", text="ID")
        self.tree.heading("nome", text="Nome")
        self.tree.heading("serie", text="Série")
        self.tree.heading("media", text="Média")

        self.tree.column("id", width=30, anchor="center")
        self.tree.column("nome", width=140)
        self.tree.column("serie", width=70, anchor="center")
        self.tree.column("media", width=60, anchor="center")

        scrollbar = ttk.Scrollbar(
            frame_tabela, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.ao_selecionar_aluno)

    def carregar_foto(self):
        caminho_arquivo = filedialog.askopenfilename(
            title="Selecionar Foto do Aluno",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.bmp")],
        )
        if caminho_arquivo:
            with open(caminho_arquivo, "rb") as f:
                self.foto_bytes = f.read()
            self.exibir_foto(self.foto_bytes)

    def exibir_foto(self, foto_bytes):
        if foto_bytes and HAS_PIL:
            import io

            img = Image.open(io.BytesIO(foto_bytes))
            img = img.resize((100, 100), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.lbl_foto.config(image=photo, text="", width=100, height=100)
            self.lbl_foto.image = photo
        else:
            self.lbl_foto.config(
                image="",
                text="Foto\nCarregada" if foto_bytes else "Sem Foto",
                width=15,
                height=5,
            )

    def salvar(self):
        nome = self.ent_nome.get().strip()
        if not nome:
            messagebox.showerror(
                "Erro", "O campo 'Nome' é obrigatório."
            )
            return

        try:
            salvar_aluno(
                nome=nome,
                data_nasc=self.ent_data_nasc.get().strip(),
                email=self.ent_email.get().strip(),
                telefone=self.ent_telefone.get().strip(),
                serie=self.ent_serie.get().strip(),
                nota1=self.ent_nota1.get().strip(),
                nota2=self.ent_nota2.get().strip(),
                foto_bytes=self.foto_bytes,
                aluno_id=self.aluno_selecionado_id,
            )
            messagebox.showinfo("Sucesso", "Aluno salvo com sucesso!")
            self.limpar_formulario()
            self.atualizar_lista()
        except ValueError as e:
            messagebox.showerror("Erro de Validação", str(e))
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao salvar: {e}")

    def atualizar_lista(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for aluno in listar_alunos():
            self.tree.insert("", "end", values=aluno)

    def ao_selecionar_aluno(self, event):
        item_selecionado = self.tree.selection()
        if not item_selecionado:
            return

        aluno_id = self.tree.item(item_selecionado[0])["values"][0]
        aluno = buscar_aluno_por_id(aluno_id)

        if aluno:
            self.aluno_selecionado_id = aluno[0]
            self.limpar_formulario(manter_id=True)

            self.ent_nome.insert(0, aluno[1] or "")
            self.ent_data_nasc.insert(0, aluno[2] or "")
            self.ent_email.insert(0, aluno[3] or "")
            self.ent_telefone.insert(0, aluno[4] or "")
            self.ent_serie.insert(0, aluno[5] or "")
            self.ent_nota1.insert(0, str(aluno[6]) if aluno[6] is not None else "")
            self.ent_nota2.insert(0, str(aluno[7]) if aluno[7] is not None else "")

            self.foto_bytes = aluno[9]
            self.exibir_foto(self.foto_bytes)

    def excluir(self):
        if not self.aluno_selecionado_id:
            messagebox.showwarning(
                "Aviso", "Selecione um aluno na tabela para excluir."
            )
            return

        confirmar = messagebox.askyesno(
            "Confirmar", "Tem certeza que deseja excluir este aluno?"
        )
        if confirmar:
            deletar_aluno(self.aluno_selecionado_id)
            messagebox.showinfo("Sucesso", "Aluno excluído!")
            self.limpar_formulario()
            self.atualizar_lista()

    def limpar_formulario(self, manter_id=False):
        if not manter_id:
            self.aluno_selecionado_id = None

        self.ent_nome.delete(0, END)
        self.ent_data_nasc.delete(0, END)
        self.ent_email.delete(0, END)
        self.ent_telefone.delete(0, END)
        self.ent_serie.delete(0, END)
        self.ent_nota1.delete(0, END)
        self.ent_nota2.delete(0, END)

        self.foto_bytes = None
        self.lbl_foto.config(
            image="", text="Sem Foto", width=15, height=5
        )
        self.lbl_foto.image = None


if __name__ == "__main__":
    root = Tk()
    app = AppCadastro(root)
    root.mainloop()
