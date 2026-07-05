export class TemplateRegistry {
  private readonly templates = new Map<string, string>();

  register(id: string, body: string): void {
    if (!id || !body) {
      throw new Error('template id and body are required');
    }
    this.templates.set(id, body);
  }

  get(id: string): string {
    const template = this.templates.get(id);
    if (!template) {
      throw new Error('template not found');
    }
    return template;
  }
}
