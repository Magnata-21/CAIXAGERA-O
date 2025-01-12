import os
from kivy.config import Config

# Configurar para usar ANGLE com OpenGL
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
Config.set('graphics', 'multisamples', '0')
Config.set('graphics', 'context', 'angle_sdl2')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.treeview import TreeView, TreeViewLabel
from kivy.uix.popup import Popup
import pickle
import os
from datetime import datetime

class CaixaGeracaoApp(App):
    def build(self):
        self.title = 'Caixa Geração de Adoradores'
        
        self.members = []
        self.values = {}
        self.entries = []
        self.total_arrecadado = 0.00
        self.total_saida_mensal = 0.00
        self.saidas = []

        self.load_data()
        self.check_end_of_month()

        self.main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.create_main_layout()

        return self.main_layout

    def create_main_layout(self):
        self.main_layout.clear_widgets()

        self.label = Label(text='Caixa Geração de Adoradores', font_size=24, size_hint=(1, 0.2))
        self.main_layout.add_widget(self.label)

        self.total_label = Label(text=f'Total Arrecadado: R$ {self.total_arrecadado:.2f}'.replace('.', ','), size_hint=(1, 0.1))
        self.main_layout.add_widget(self.total_label)

        self.saida_label = Label(text=f'Saída Mensal: R$ {self.total_saida_mensal:.2f}'.replace('.', ','), size_hint=(1, 0.1))
        self.main_layout.add_widget(self.saida_label)

        add_member_button = Button(text='Cadastro', size_hint=(1, 0.1), on_release=self.cadastro)
        self.main_layout.add_widget(add_member_button)

        add_entry_button = Button(text='Entrada', size_hint=(1, 0.1), on_release=self.entrada)
        self.main_layout.add_widget(add_entry_button)

        add_exit_button = Button(text='Saída', size_hint=(1, 0.1), on_release=self.saida)
        self.main_layout.add_widget(add_exit_button)

        exit_button = Button(text='Sair', size_hint=(1, 0.1), on_release=self.stop)
        self.main_layout.add_widget(exit_button)

    def inicio(self, instance):
        self.main_layout.clear_widgets()
        self.create_main_layout()  # Reconstrói a interface principal

    def cadastro(self, instance):
        self.main_layout.clear_widgets()

        # Exibir membros cadastrados
        self.members_tree = TreeView(root_options={'text': 'Membros Cadastrados'}, hide_root=False)
        for member in self.members:
            self.members_tree.add_node(TreeViewLabel(text=f"{member[0]} {member[1]} - {member[2]}"))
        self.main_layout.add_widget(self.members_tree)

        add_button = Button(text="Adicionar Membro", size_hint=(1, 0.1), on_release=self.novo_membro)
        self.main_layout.add_widget(add_button)

        remove_button = Button(text="Remover Membro", size_hint=(1, 0.1), on_release=self.remover_membro)
        self.main_layout.add_widget(remove_button)

        inicio_button = Button(text="Início", size_hint=(1, 0.1), on_release=self.inicio)
        self.main_layout.add_widget(inicio_button)

    def novo_membro(self, instance):
        novo_membro_popup = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.name_input = TextInput(hint_text="Nome Completo")
        novo_membro_popup.add_widget(self.name_input)
        self.birth_input = TextInput(hint_text="Aniversário (DDMMYYYY)")
        novo_membro_popup.add_widget(self.birth_input)
        add_button = Button(text="Adicionar", size_hint=(1, 0.2), on_release=lambda x: self.adicionar_membro())
        novo_membro_popup.add_widget(add_button)

        popup = Popup(title="Novo Membro", content=novo_membro_popup, size_hint=(0.8, 0.8))
        add_button.bind(on_release=popup.dismiss)
        popup.open()

    def adicionar_membro(self):
        nome_completo = self.name_input.text
        aniversario = self.birth_input.text
        if nome_completo and aniversario:
            nome_completo_split = nome_completo.split()
            nome = nome_completo_split[0]
            sobrenome = " ".join(nome_completo_split[1:]) if len(nome_completo_split) > 1 else ""
            aniversario = f"{aniversario[:2]}/{aniversario[2:4]}/{aniversario[4:]}"
            self.members.append((nome, sobrenome, aniversario))
            self.values[(nome, sobrenome, aniversario)] = 0.00
            self.save_data()
            self.cadastro(None)

    def remover_membro(self, instance):
        selected_node = self.members_tree.selected_node
        if selected_node:
            member_text = selected_node.text
            member_name, _, aniversario = member_text.partition(" - ")
            nome, sobrenome = member_name.split(maxsplit=1)
            member = (nome, sobrenome, aniversario)
            self.members.remove(member)
            self.values.pop(member, None)
            self.save_data()
            self.cadastro(None)

    def entrada(self, instance):
        self.main_layout.clear_widgets()

        # Exibir entradas registradas
        self.entries_tree = TreeView(root_options={'text': 'Entradas Registradas'}, hide_root=False)
        for entry in self.entries:
            self.entries_tree.add_node(TreeViewLabel(text=f"{entry[0]} - R$ {entry[1]:.2f}".replace('.', ',')))
        self.main_layout.add_widget(self.entries_tree)

        add_button = Button(text="Adicionar Entrada", size_hint=(1, 0.1), on_release=self.nova_entrada)
        self.main_layout.add_widget(add_button)

        remove_button = Button(text="Remover Entrada", size_hint=(1, 0.1), on_release=self.remover_entrada)
        self.main_layout.add_widget(remove_button)

        inicio_button = Button(text="Início", size_hint=(1, 0.1), on_release=self.inicio)
        self.main_layout.add_widget(inicio_button)

    def nova_entrada(self, instance):
        nova_entrada_popup = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.member_input = TextInput(hint_text="Nome do Membro")
        nova_entrada_popup.add_widget(self.member_input)
        self.value_input = TextInput(hint_text="Valor")
        nova_entrada_popup.add_widget(self.value_input)
        add_button = Button(text="Adicionar", size_hint=(1, 0.2), on_release=lambda x: self.adicionar_valor())
        nova_entrada_popup.add_widget(add_button)

        popup = Popup(title="Nova Entrada", content=nova_entrada_popup, size_hint=(0.8, 0.8))
        add_button.bind(on_release=popup.dismiss)
        popup.open()

    def adicionar_valor(self):
        member_name = self.member_input.text
        value_str = self.value_input.text
        try:
            value = float(value_str.replace(',', '.'))
            found_member = None
            for member in self.members:
                if f"{member[0]} {member[1]}" == member_name:
                    found_member = member
                    break

            if found_member:
                if found_member in self.values:
                    self.values[found_member] += value
                else:
                    self.values[found_member] = value
                self.total_arrecadado += value
                self.entries.append((member_name, value))
                self.save_data()
                self.entrada(None)
            else:
                popup = Popup(title="Erro", content=Label(text="Membro não encontrado. Por favor, cadastre o membro primeiro."), size_hint=(0.8, 0.8))
                popup.open()
        except ValueError:
            popup = Popup(title="Erro", content=Label(text="Valor inválido. Por favor, insira um número."), size_hint=(0.8, 0.8))
            popup.open()

    def remover_entrada(self, instance):
        selected_node = self.entries_tree.selected_node
        if selected_node:
            entry_text = selected_node.text
            member_name, _, valor = entry_text.partition(" - R$ ")
            valor = float(valor.replace(',', '.'))
            self.entries = [entry for entry in self.entries if entry != (member_name, valor)]
            found_member = None
            for member in self.members:
                if f"{member[0]} {member[1]}" == member_name:
                    found_member = member
                    break

            if found_member:
                self.values[found_member] -= valor
                if self.values[found_member] == 0:
                    del self.values[found_member]
                self.total_arrecadado -= valor
                self.save_data()
                self.entrada(None)

    def saida(self, instance):
        self.main_layout.clear_widgets()

        # Exibir saídas registradas
        self.saidas_tree = TreeView(root_options={'text': 'Saídas Registradas'}, hide_root=False)
        for saida in self.saidas:
            self.saidas_tree.add_node(TreeViewLabel(text=f"R$ {saida[0]:.2f}".replace('.', ',') + " - " + saida[1] + " - " + saida[2]))
            self.main_layout.add_widget(self.saidas_tree)

        add_button = Button(text="Adicionar Saída", size_hint=(1, 0.1), on_release=self.nova_saida)
        self.main_layout.add_widget(add_button)

        remove_button = Button(text="Remover Saída", size_hint=(1, 0.1), on_release=self.remover_saida)
        self.main_layout.add_widget(remove_button)

        inicio_button = Button(text="Início", size_hint=(1, 0.1), on_release=self.inicio)
        self.main_layout.add_widget(inicio_button)

    def nova_saida(self, instance):
        nova_saida_popup = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.saida_value_input = TextInput(hint_text="Valor")
        nova_saida_popup.add_widget(self.saida_value_input)
        self.saida_local_input = TextInput(hint_text="Local")
        nova_saida_popup.add_widget(self.saida_local_input)
        self.saida_date_input = TextInput(hint_text="Data (DD/MM/AAAA)")
        nova_saida_popup.add_widget(self.saida_date_input)
        add_button = Button(text="Adicionar", size_hint=(1, 0.2), on_release=lambda x: self.adicionar_saida())
        nova_saida_popup.add_widget(add_button)
        
        popup = Popup(title="Nova Saída", content=nova_saida_popup, size_hint=(0.8, 0.8))
        add_button.bind(on_release=popup.dismiss)
        popup.open()

    def adicionar_saida(self):
        valor_str = self.saida_value_input.text
        local = self.saida_local_input.text
        data = self.saida_date_input.text
        try:
            valor = float(valor_str.replace(',', '.'))
            self.total_saida_mensal += valor
            self.total_arrecadado -= valor
            self.saidas.append((valor, local, data))
            self.save_data()
            self.saida(None)
        except ValueError:
            popup = Popup(title="Erro", content=Label(text="Valor inválido. Por favor, insira um número."), size_hint=(0.8, 0.8))
            popup.open()

    def remover_saida(self, instance):
        selected_node = self.saidas_tree.selected_node
        if selected_node:
            saida_text = selected_node.text
            valor, local, data = saida_text.split(" - ")
            valor = float(valor.replace('R$ ', '').replace(',', '.'))
            for saida in self.saidas:
                if saida == (valor, local, data):
                    self.saidas.remove(saida)
                    self.total_saida_mensal -= valor
                    self.total_arrecadado += valor
                    self.save_data()
                    self.saida(None)
                    return
            popup = Popup(title="Erro", content=Label(text="Saída não encontrada."), size_hint=(0.8, 0.8))
            popup.open()

    def voltar_inicio(self, instance):
        self.main_layout.clear_widgets()
        self.build()  # Reconstrói a interface principal


    def save_data(self):
        data = {
            'members': self.members,
            'values': self.values,
            'entries': self.entries,
            'total_arrecadado': self.total_arrecadado,
            'total_saida_mensal': self.total_saida_mensal,
            'saidas': self.saidas
        }
        with open('data.pk2', 'wb') as f:
            pickle.dump(data, f)

    def load_data(self):
        if os.path.exists('data.pk2'):
            with open('data.pk2', 'rb') as f:
                data = pickle.load(f)
                self.members = data.get('members', [])
                self.values = data.get('values', {})
                self.entries = data.get('entries', [])
                self.total_arrecadado = data.get('total_arrecadado', 0.00)
                self.total_saida_mensal = data.get('total_saida_mensal', 0.00)
                self.saidas = data.get('saidas', [])

    def check_end_of_month(self):
        today = datetime.today()
        if today.day == 1:
            self.total_saida_mensal = 0.00  # Zerar saída mensal no primeiro dia do mês
            for member in self.members:
                self.values[member] = 0.00  # Zerar valores recebidos

if __name__ == "__main__":
    CaixaGeracaoApp().run()
