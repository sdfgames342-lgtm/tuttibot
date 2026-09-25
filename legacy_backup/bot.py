from playwright.sync_api import sync_playwright
import time

URL_LOGIN = "https://srvcnpc.policia.gov.co/CNPC/Login.aspx"
USER = "13507592"
PASS = "dvvVonVfOj"

def test_login_definitivo():
    print("Iniciando motor Chromium Stealth...")
    with sync_playwright() as p:
        # Lanzamos el navegador en modo 'headless=False' para que VEAS lo que hace
        # Una vez confirmes que funciona, puedes poner headless=True para que corra oculto
        browser = p.chromium.launch(headless=False) 
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        print("1. Accediendo a la URL de Login...")
        page.goto(URL_LOGIN, wait_until="networkidle")
        
        # Esperamos a que los campos existan para asegurar que el JS cargó
        page.wait_for_selector("#txtUsuario", timeout=10000)
        
        print("2. Inyectando credenciales...")
        page.fill("#txtUsuario", USER)
        page.fill("#txtClave", PASS)
        
        print("3. Ejecutando Submit...")
        # Hacemos clic y esperamos que la página cambie (navegación)
        page.click("#btnIngresar")
        
        # Damos unos segundos para que el servidor procese la redirección ASP.NET
        time.sleep(5)
        
        print(f"4. URL actual tras el Login: {page.url}")
        
        # Validamos si logramos salir de la página de Login
        if "Login.aspx" not in page.url:
            print("✅ ACCESO CONCEDIDO: El WAF ha sido superado.")
            
            # Buscamos el nombre del usuario para confirmar
            try:
                nombre = page.locator("#ctl00_lblUsuario").inner_text()
                print(f"👤 Funcionario detectado: {nombre}")
            except:
                print("⚠️ No se encontró el nombre en pantalla, pero se superó el login.")
                
            # Extraemos las cookies "mágicas" que ahora son 100% válidas
            cookies = context.cookies()
            print("\n🍪 Cookies de sesión obtenidas:")
            for c in cookies:
                print(f"{c['name']} = {c['value']}")
                
        else:
            print("🚫 ACCESO DENEGADO: El servidor rechazó las credenciales o detectó el bot.")
            # Tomamos una captura para ver qué pasó (ej. un Captcha apareció)
            page.screenshot(path="error_pantalla_login.png")
            print("📸 Se ha guardado una captura del error en 'error_pantalla_login.png'")

        browser.close()

if __name__ == "__main__":
    test_login_definitivo()