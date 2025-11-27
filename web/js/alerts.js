// Alerts helper library
// Exposes global `Alerts` with methods:
// - Alerts.showToast(message, {type:'info'|'success', ttl:ms, meta})
// - Alerts.sendNotification({to, message, persist}) -> Promise<Response>
// - Alerts.initSocket(options) -> initializes socket client and shows incoming notifications
// Designed to be included via <script src="/js/alerts.js"></script>
(function(global){
    if(global.Alerts) return; // don't overwrite

    // inject minimal styles for toasts
    function injectStyles(){
        if(document.getElementById('alerts-styles')) return;
        const css = `
        #toastContainer{position:fixed;top:18px;right:18px;display:flex;flex-direction:column;gap:10px;z-index:99999;pointer-events:none;max-width:360px}
        .toast{pointer-events:auto;background:#fff;color:#111;border-radius:8px;box-shadow:0 8px 20px rgba(0,0,0,0.12);padding:12px 14px;transform:translateY(-6px) scale(.995);opacity:0;transition:transform 240ms cubic-bezier(.2,.9,.3,1),opacity 240ms ease-in-out;font-size:14px}
        .toast.show{transform:translateY(0) scale(1);opacity:1}
        .toast.hide{opacity:0;transform:translateY(-8px) scale(.995)}
        .toast.success{background:#e6ffed;border:1px solid #b7f1c6;color:#0b7a3a}
        .toast.info{background:#eef6ff;border:1px solid #cde3ff;color:#0b4f9a}
        .toast .meta{display:block;font-size:12px;color:rgba(0,0,0,0.6);margin-top:6px}
        `;
        const s = document.createElement('style');
        s.id = 'alerts-styles';
        s.appendChild(document.createTextNode(css));
        document.head.appendChild(s);
    }

    function getContainer(){
        let c = document.getElementById('toastContainer');
        if(!c){ c = document.createElement('div'); c.id = 'toastContainer'; c.setAttribute('aria-live','polite'); c.setAttribute('aria-atomic','true'); document.body.appendChild(c); }
        return c;
    }

    function escapeHtml(s){
        return s.replace(/[&<>\"]/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; });
    }

    function showToast(message, opts){
        opts = opts || {};
        injectStyles();
        const container = getContainer();
        const t = document.createElement('div');
        t.className = 'toast ' + (opts.type || 'info');
        t.innerHTML = `<div class="msg">${escapeHtml(String(message))}</div>`;
        if(opts.meta){ const m = document.createElement('div'); m.className='meta'; m.textContent = opts.meta; t.appendChild(m); }
        container.prepend(t);
        // animate in
        requestAnimationFrame(()=> t.classList.add('show'));
        const ttl = (typeof opts.ttl === 'number') ? opts.ttl : 10000;
        const hide = ()=>{ t.classList.remove('show'); t.classList.add('hide'); setTimeout(()=> t.remove(), 300); };
        const timeoutId = setTimeout(hide, ttl);
        t.addEventListener('click', ()=>{ clearTimeout(timeoutId); hide(); });
        return t;
    }

    function loadScript(src, cb){
        const s = document.createElement('script'); s.src = src; s.async = true;
        s.onload = ()=> cb(null); s.onerror = (e)=> cb(e||new Error('load error')); document.head.appendChild(s);
    }

    // initialize socket.io client and listen for `notificacion` events
    function initSocket(options){
        options = options || {};
        // if io already present, init immediately
        function doInit(){
            try{
                const socket = (options.ioFactory && typeof options.ioFactory === 'function') ? options.ioFactory() : io();
                socket.on('connect', ()=>{ if(options.onConnect) options.onConnect(); });
                socket.on('connect_error', (err)=>{ console.error('Socket connect error', err); showToast('Error conectando a notificaciones', {type:'info', ttl:8000}); if(options.onError) options.onError(err); });
                socket.on('notificacion', (payload)=>{
                    console.log(payload.mensaje);
                    try{const m = payload.mensaje; showToast(m, {type:'success', ttl:10000}); }catch(e){ showToast('Notificación recibida', {type:'success', ttl:10000}); }
                });
                // expose
                Alerts.socket = socket;
                return socket;
            }catch(e){ console.error('initSocket error', e); }
        }

        if(typeof io === 'undefined'){
            const cdn = options.cdn || 'https://cdn.socket.io/4.6.1/socket.io.min.js';
            loadScript(cdn, function(err){
                if(err){ // try local
                    loadScript('/socket.io/socket.io.js', function(err2){ if(err2){ console.error('Could not load socket.io client'); showToast('No se pudo cargar Socket.IO client', {type:'info', ttl:8000}); } else { doInit(); } });
                } else { doInit(); }
            });
        } else {
            return doInit();
        }
    }

    // Sends notification via API; tries /api/notify first, falls back to /test/notify
    function sendNotification(payload){
        payload = payload || {};
        const body = JSON.stringify(payload);
        return fetch('/api/notify', {method:'POST', headers:{'Content-Type':'application/json'}, body: body})
        .then(res=>{
            if(res.status === 401 || res.status === 403) return fetch('/test/notify', {method:'POST', headers:{'Content-Type':'application/json'}, body: body});
            return res;
        })
        .catch(err=>{
            // fallback to test endpoint
            return fetch('/test/notify', {method:'POST', headers:{'Content-Type':'application/json'}, body: body});
        });
    }

    const Alerts = {
        showToast: showToast,
        initSocket: initSocket,
        sendNotification: sendNotification,
        socket: null
    };

    global.Alerts = Alerts;
})(window);
