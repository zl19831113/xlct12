// Audio compatibility fix script
document.addEventListener('DOMContentLoaded', function() {
    console.log("Running audio compatibility fix...");
    
    // Override the createAudioPlayer function to add compatibility checks
    const originalCreateAudioPlayer = window.createAudioPlayer;
    window.createAudioPlayer = function(audioId, audioUrl) {
        console.log("Creating audio player with enhanced compatibility:", audioId, audioUrl);
        
        // If original URL doesn't work, try to fix it
        const fixAudioUrl = (url) => {
            // Add timestamp to prevent caching issues
            if (url.includes('?')) {
                return `${url}&t=${Date.now()}`;
            } else {
                return `${url}?t=${Date.now()}`;
            }
        };
        
        // Call the original function with fixed URL
        const player = originalCreateAudioPlayer(audioId, fixAudioUrl(audioUrl));
        
        // Add additional error handling to the player
        const originalAudio = audioPlayers.get(audioId);
        if (originalAudio && originalAudio.audio) {
            const audio = originalAudio.audio;
            
            // Enhanced error handling
            audio.addEventListener('error', function(e) {
                console.error("Audio error occurred:", e);
                const errorCode = e.target.error ? e.target.error.code : 'unknown';
                console.log(`Audio error code: ${errorCode}`);
                
                // Try alternative format if MP3 fails
                if (!audioUrl.includes('&format=mp3')) {
                    console.log("Trying alternative audio format...");
                    const newUrl = audioUrl.includes('?') 
                        ? `${audioUrl}&format=mp3` 
                        : `${audioUrl}?format=mp3`;
                    
                    // Replace the source
                    audio.src = newUrl;
                    audio.load();
                    audio.play().catch(err => console.error("Still failed after format change:", err));
                }
            });
            
            // Force reload if audio is stuck
            audio.addEventListener('stalled', function() {
                console.log("Audio stalled, reloading...");
                audio.load();
            });
        }
        
        return player;
    };
    
    // Patch toggleAudioPlay for better error handling
    const originalToggleAudioPlay = window.toggleAudioPlay;
    window.toggleAudioPlay = function(id, url) {
        console.log("Enhanced audio toggle:", id, url);
        
        try {
            // If URL is relative and doesn't start with slash, add it
            if (url && !url.startsWith('/') && !url.startsWith('http')) {
                url = '/' + url;
            }
            
            return originalToggleAudioPlay(id, url);
        } catch (err) {
            console.error("Toggle audio play error:", err);
            alert("音频播放失败，请尝试刷新页面。");
        }
    };
});
