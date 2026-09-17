import { App, Plugin, PluginSettingTab, Setting, Notice } from 'obsidian';

interface TensorFlowSyncSettings {
    apiUrl: string;
    autoSync: boolean;
    syncInterval: number;
    notebookPath: string;
}

const DEFAULT_SETTINGS: TensorFlowSyncSettings = {
    apiUrl: 'http://localhost:3001',
    autoSync: true,
    syncInterval: 60,
    notebookPath: 'TensorFlow Intelligence'
}

export default class TensorFlowSyncPlugin extends Plugin {
    settings: TensorFlowSyncSettings;
    syncInterval: number;

    async onload() {
        await this.loadSettings();

        // Comando: Sincronizar Ahora
        this.addCommand({
            id: 'sync-tensorflow-data',
            name: 'Sincronizar con TensorFlow API',
            callback: () => {
                this.syncData();
            }
        });

        // Comando: Crear Reporte Semanal
        this.addCommand({
            id: 'create-weekly-report',
            name: 'Crear Reporte Semanal',
            callback: () => {
                this.createWeeklyReport();
            }
        });

        // Comando: Registrar Decisión
        this.addCommand({
            id: 'register-decision',
            name: 'Registrar Decisión Personal',
            callback: () => {
                this.registerDecision();
            }
        });

        // Auto-sync si está habilitado
        if (this.settings.autoSync) {
            this.syncInterval = window.setInterval(
                () => this.syncData(),
                this.settings.syncInterval * 60 * 1000
            );
        }

        // Agregar ícono en ribbon
        this.addRibbonIcon('brain-circuit', 'TensorFlow Sync', () => {
            this.syncData();
        });

        // Settings tab
        this.addSettingTab(new TensorFlowSyncSettingTab(this.app, this));

        new Notice('TensorFlow Intelligence Sync activado');
    }

    async syncData() {
        try {
            // Verificar conexión
            const healthResponse = await fetch(`${this.settings.apiUrl}/health`);
            if (!healthResponse.ok) {
                new Notice('❌ No se puede conectar a TensorFlow API');
                return;
            }

            // Obtener datos de Power BI
            const dataResponse = await fetch(`${this.settings.apiUrl}/api/integrations/powerbi-data`);
            const data = await dataResponse.json();

            // Crear/actualizar nota de métricas
            await this.updateMetricsNote(data);

            new Notice('✅ Datos sincronizados correctamente');
        } catch (error) {
            new Notice(`❌ Error en sincronización: ${error.message}`);
        }
    }

    async updateMetricsNote(data: any) {
        const folderPath = this.settings.notebookPath;
        const notePath = `${folderPath}/Métricas Actuales.md`;

        // Crear folder si no existe
        if (!await this.app.vault.adapter.exists(folderPath)) {
            await this.app.vault.createFolder(folderPath);
        }

        const content = `# Métricas TensorFlow Intelligence System

> Última actualización: ${new Date().toLocaleString('es-MX')}

## 🏗️ Inmobiliario

- **Desarrollos analizados**: ${data.real_estate.desarrollos_analizados}
- **Oportunidades alta prioridad**: ${data.real_estate.oportunidades_alta_prioridad}
- **Tasa de éxito**: ${(data.real_estate.tasa_exito_predicciones * 100).toFixed(0)}%

## 📱 Redes Sociales

- **Posts analizados**: ${data.social_media.posts_analizados}
- **Engagement promedio**: ${data.social_media.engagement_promedio}
- **Posts virales predichos**: ${data.social_media.posts_virales_predichos}

## 🎯 Personal

- **Decisiones optimizadas**: ${data.personal.decisiones_optimizadas}
- **Ahorro total estimado**: $${data.personal.ahorro_total_estimado.toLocaleString()}

---

*Sincronizado automáticamente desde TensorFlow API*
`;

        // Crear o actualizar nota
        if (await this.app.vault.adapter.exists(notePath)) {
            const file = this.app.vault.getAbstractFileByPath(notePath);
            await this.app.vault.modify(file as any, content);
        } else {
            await this.app.vault.create(notePath, content);
        }
    }

    async createWeeklyReport() {
        try {
            // Obtener calendario semanal
            const response = await fetch(`${this.settings.apiUrl}/api/generate/weekly-content-schedule`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    temas_disponibles: ['Cap Rate', 'Estrategia Inmobiliaria', 'Caso UIA', 'ExO', 'Tenis']
                })
            });

            const data = await response.json();
            
            // Crear nota con reporte
            const folderPath = this.settings.notebookPath;
            const date = new Date();
            const notePath = `${folderPath}/Reportes Semanales/Semana ${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}.md`;

            let content = `# Reporte Semanal TensorFlow\n\n`;
            content += `> Generado: ${date.toLocaleString('es-MX')}\n\n`;
            content += `## 📅 Calendario de Contenido\n\n`;

            for (const dia of data.semana) {
                content += `### ${dia.dia}\n\n`;
                for (const post of dia.posts) {
                    content += `- **${String(post.hora).padStart(2, '0')}:00** - ${post.tipo} sobre "${post.tema}"\n`;
                    content += `  - Engagement esperado: ${post.engagement_esperado.toFixed(1)}/100\n`;
                    content += `  - Probabilidad viral: ${(post.prob_viral * 100).toFixed(1)}%\n\n`;
                }
            }

            content += `\n## 📊 Resumen\n\n`;
            content += `- Total posts: ${data.resumen.total_posts_recomendados}\n`;
            content += `- Mejor día: ${data.resumen.mejor_dia}\n`;
            content += `- Temas cubiertos: ${data.resumen.temas_cubiertos}\n`;

            // Crear folder si no existe
            const weeklyFolder = `${folderPath}/Reportes Semanales`;
            if (!await this.app.vault.adapter.exists(weeklyFolder)) {
                await this.app.vault.createFolder(weeklyFolder);
            }

            await this.app.vault.create(notePath, content);
            new Notice('✅ Reporte semanal creado');

        } catch (error) {
            new Notice(`❌ Error al crear reporte: ${error.message}`);
        }
    }

    async registerDecision() {
        // Crear template de decisión
        const folderPath = this.settings.notebookPath;
        const decisionsFolder = `${folderPath}/Decisiones`;
        const date = new Date();
        const notePath = `${decisionsFolder}/Decisión ${date.toISOString().split('T')[0]}.md`;

        const content = `# Decisión Personal

> Fecha: ${date.toLocaleString('es-MX')}

## 🎯 Contexto

- **Área**: (Inmobiliario / Personal / Familia)
- **Decisión**: 

## 📊 Datos de TensorFlow

- **Predicción**: 
- **Probabilidad**: 
- **Recomendación**: 

## 💭 Reflexión

### ¿Por qué esta decisión?



### Resultado esperado



### Aprendizajes



---

*Tags*: #decision #tensorflow #aprendizaje
`;

        // Crear folder si no existe
        if (!await this.app.vault.adapter.exists(decisionsFolder)) {
            await this.app.vault.createFolder(decisionsFolder);
        }

        const file = await this.app.vault.create(notePath, content);
        
        // Abrir la nota
        const leaf = this.app.workspace.getLeaf();
        await leaf.openFile(file);

        new Notice('✅ Template de decisión creado');
    }

    onunload() {
        if (this.syncInterval) {
            window.clearInterval(this.syncInterval);
        }
    }

    async loadSettings() {
        this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
    }

    async saveSettings() {
        await this.saveData(this.settings);
    }
}

class TensorFlowSyncSettingTab extends PluginSettingTab {
    plugin: TensorFlowSyncPlugin;

    constructor(app: App, plugin: TensorFlowSyncPlugin) {
        super(app, plugin);
        this.plugin = plugin;
    }

    display(): void {
        const { containerEl } = this;
        containerEl.empty();

        containerEl.createEl('h2', { text: 'TensorFlow Intelligence Sync' });

        new Setting(containerEl)
            .setName('API URL')
            .setDesc('URL de la API de TensorFlow')
            .addText(text => text
                .setPlaceholder('http://localhost:3001')
                .setValue(this.plugin.settings.apiUrl)
                .onChange(async (value) => {
                    this.plugin.settings.apiUrl = value;
                    await this.plugin.saveSettings();
                }));

        new Setting(containerEl)
            .setName('Auto-sincronización')
            .setDesc('Sincronizar automáticamente en segundo plano')
            .addToggle(toggle => toggle
                .setValue(this.plugin.settings.autoSync)
                .onChange(async (value) => {
                    this.plugin.settings.autoSync = value;
                    await this.plugin.saveSettings();
                    
                    // Reiniciar plugin para aplicar cambios
                    if (value && !this.plugin.syncInterval) {
                        this.plugin.syncInterval = window.setInterval(
                            () => this.plugin.syncData(),
                            this.plugin.settings.syncInterval * 60 * 1000
                        );
                    } else if (!value && this.plugin.syncInterval) {
                        window.clearInterval(this.plugin.syncInterval);
                        this.plugin.syncInterval = null;
                    }
                }));

        new Setting(containerEl)
            .setName('Intervalo de sincronización')
            .setDesc('Minutos entre sincronizaciones automáticas')
            .addText(text => text
                .setPlaceholder('60')
                .setValue(String(this.plugin.settings.syncInterval))
                .onChange(async (value) => {
                    const num = parseInt(value);
                    if (!isNaN(num) && num > 0) {
                        this.plugin.settings.syncInterval = num;
                        await this.plugin.saveSettings();
                    }
                }));

        new Setting(containerEl)
            .setName('Carpeta de notas')
            .setDesc('Ruta donde guardar las notas de TensorFlow')
            .addText(text => text
                .setPlaceholder('TensorFlow Intelligence')
                .setValue(this.plugin.settings.notebookPath)
                .onChange(async (value) => {
                    this.plugin.settings.notebookPath = value;
                    await this.plugin.saveSettings();
                }));
    }
}
