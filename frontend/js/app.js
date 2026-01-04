const ws = new WebSocket('ws://localhost:8000/subscribe');
ws.onopen = () => { console.log('WebSocket connected!'); }
ws.onmessage = (msg) => { console.log('Received:', msg.data); };