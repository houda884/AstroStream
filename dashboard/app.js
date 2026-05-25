const video = document.getElementById("video");
const canvas = document.getElementById("overlay");
const ctx = canvas.getContext("2d");
const debug = document.getElementById("debug");

const signaling = new WebSocket("ws://127.0.0.1:8765");
const pc = new RTCPeerConnection();

let dataChannel = null;

/* =========================
   Overlay : obstacles + TTC
========================= */
function drawBoxes(detections) {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  ctx.strokeStyle = "red";
  ctx.fillStyle = "red";
  ctx.lineWidth = 2;
  ctx.font = "16px Arial";

  detections.forEach((obj) => {
    ctx.strokeRect(obj.x, obj.y, obj.w, obj.h);

    if (obj.ttc !== null && obj.ttc !== undefined) {
      ctx.fillText(
        `TTC: ${obj.ttc}s`,
        obj.x + obj.w + 8,
        obj.y + 20
      );
    }
  });

  debug.textContent = JSON.stringify(detections, null, 2);
}

/* =========================
   DataChannel
========================= */
function setupDataChannel(channel) {
  dataChannel = channel;

  dataChannel.onopen = () => {
    console.log("✅ DataChannel ouvert côté dashboard");
  };

  dataChannel.onmessage = (event) => {
    const message = JSON.parse(event.data);

    if (message.type === "detections") {
      drawBoxes(message.data);
    }
  };

  dataChannel.onerror = (err) => {
    console.error("❌ Erreur DataChannel:", err);
  };

  dataChannel.onclose = () => {
    console.log("⚠️ DataChannel fermé côté dashboard");
    debug.textContent = "⚠️ Connexion perdue";
  };
}

pc.ondatachannel = (event) => {
  console.log("✅ DataChannel reçu côté dashboard");
  setupDataChannel(event.channel);
};

/* =========================
   Réception vidéo WebRTC
========================= */
async function forcePlayVideo() {
  try {
    video.muted = true;
    video.autoplay = true;
    video.playsInline = true;
    await video.play();
    console.log("✅ Lecture vidéo démarrée");
  } catch (err) {
    console.error("❌ video.play() a échoué :", err);
  }
}

pc.ontrack = (event) => {
  console.log("🎥 Track vidéo reçu");

  const stream = event.streams[0];
  const track = event.track;

  video.srcObject = stream;
  video.muted = true;
  video.autoplay = true;
  video.playsInline = true;

  video.onloadedmetadata = () => {
    forcePlayVideo();
  };

  track.onunmute = () => {
    console.log("✅ Track unmuted");
    forcePlayVideo();
  };

  setTimeout(() => forcePlayVideo(), 300);
  setTimeout(() => forcePlayVideo(), 1000);
};

pc.oniceconnectionstatechange = () => {
  console.log("ICE connection state:", pc.iceConnectionState);
};

pc.onconnectionstatechange = () => {
  console.log("Peer connection state:", pc.connectionState);

  if (
    pc.connectionState === "failed" ||
    pc.connectionState === "disconnected" ||
    pc.connectionState === "closed"
  ) {
    debug.textContent = "⚠️ Connexion WebRTC perdue";
  }
};

pc.onicecandidate = (event) => {
  if (event.candidate) {
    signaling.send(JSON.stringify({
      type: "ice-candidate",
      candidate: event.candidate,
    }));
  }
};

function waitForIceGatheringComplete(pc) {
  return new Promise((resolve) => {
    if (pc.iceGatheringState === "complete") {
      resolve();
    } else {
      function checkState() {
        if (pc.iceGatheringState === "complete") {
          pc.removeEventListener("icegatheringstatechange", checkState);
          resolve();
        }
      }
      pc.addEventListener("icegatheringstatechange", checkState);
    }
  });
}

/* =========================
   Signaling WebSocket
========================= */
signaling.onopen = () => {
  console.log("Connecté au signaling");
  signaling.send(JSON.stringify({ type: "register", role: "dashboard" }));
};

signaling.onmessage = async (event) => {
  const data = JSON.parse(event.data);
  console.log("Message signaling reçu:", data);

  if (data.type === "offer") {
    await pc.setRemoteDescription({
      type: data.sdpType,
      sdp: data.sdp,
    });

    const answer = await pc.createAnswer();
    await pc.setLocalDescription(answer);

    await waitForIceGatheringComplete(pc);

    signaling.send(JSON.stringify({
      type: "answer",
      sdp: pc.localDescription.sdp,
      sdpType: pc.localDescription.type,
    }));
  }

  if (data.type === "ice-candidate" && data.candidate) {
    try {
      await pc.addIceCandidate(data.candidate);
    } catch (err) {
      console.error("Erreur addIceCandidate:", err);
    }
  }
};

signaling.onerror = (err) => {
  console.error("Erreur WebSocket signaling:", err);
};

/* =========================
   Contrôle clavier dashboard
========================= */
const keyboardState = {
  left: false,
  right: false,
  up: false,
  down: false,
};

function buildCommand() {
  let steering = 0;
  let throttle = 0;
  let brake = 0;

  if (keyboardState.left) steering = -1;
  if (keyboardState.right) steering = 1;
  if (keyboardState.up) throttle = 1;
  if (keyboardState.down) brake = 1;

  return {
    type: "command",
    data: {
      steering,
      throttle,
      brake,
    },
  };
}

function sendCurrentCommand() {
  if (!dataChannel || dataChannel.readyState !== "open") return;

  const command = buildCommand();
  console.log("📤 Commande envoyée:", command);
  dataChannel.send(JSON.stringify(command));
}

window.addEventListener("keydown", (event) => {
  if (["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"].includes(event.key)) {
    event.preventDefault();
  }

  let changed = false;

  if (event.key === "ArrowLeft" && !keyboardState.left) {
    keyboardState.left = true;
    changed = true;
  }
  if (event.key === "ArrowRight" && !keyboardState.right) {
    keyboardState.right = true;
    changed = true;
  }
  if (event.key === "ArrowUp" && !keyboardState.up) {
    keyboardState.up = true;
    changed = true;
  }
  if (event.key === "ArrowDown" && !keyboardState.down) {
    keyboardState.down = true;
    changed = true;
  }

  if (changed) {
    sendCurrentCommand();
  }
});

window.addEventListener("keyup", (event) => {
  if (["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"].includes(event.key)) {
    event.preventDefault();
  }

  let changed = false;

  if (event.key === "ArrowLeft" && keyboardState.left) {
    keyboardState.left = false;
    changed = true;
  }
  if (event.key === "ArrowRight" && keyboardState.right) {
    keyboardState.right = false;
    changed = true;
  }
  if (event.key === "ArrowUp" && keyboardState.up) {
    keyboardState.up = false;
    changed = true;
  }
  if (event.key === "ArrowDown" && keyboardState.down) {
    keyboardState.down = false;
    changed = true;
  }

  if (changed) {
    sendCurrentCommand();
  }
});