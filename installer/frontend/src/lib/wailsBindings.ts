type WailsWindow = {
  go: { main: { App: { OpenBrowser: (url: string) => Promise<void> } } };
};

export function openBrowser(url: string): Promise<void> {
  return (window as unknown as WailsWindow).go.main.App.OpenBrowser(url);
}
