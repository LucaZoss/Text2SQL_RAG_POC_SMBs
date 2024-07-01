async function signInWithGoogle() {
    const provider = new firebase.auth.GoogleAuthProvider();
    try {
        const result = await firebase.auth().signInWithPopup(provider);
        const idToken = await result.user.getIdToken();
        // Store idToken in local storage or cookie
        document.cookie = `token=${idToken}`;
        window.location.href = '/';
    } catch (error) {
        console.error(error);
    }
}

async function signInWithApple() {
    const provider = new firebase.auth.OAuthProvider('apple.com');
    try {
        const result = await firebase.auth().signInWithPopup(provider);
        const idToken = await result.user.getIdToken();
        // Store idToken in local storage or cookie
        document.cookie = `token=${idToken}`;
        window.location.href = '/';
    } catch (error) {
        console.error(error);
    }
}

async function registerWithGoogle() {
    const provider = new firebase.auth.GoogleAuthProvider();
    try {
        const result = await firebase.auth().createUserWithPopup(provider);
        const idToken = await result.user.getIdToken();
        // Store idToken in local storage or cookie
        document.cookie = `token=${idToken}`;
        window.location.href = '/';
    } catch (error) {
        console.error(error);
    }
}

async function registerWithApple() {
    const provider = new firebase.auth.OAuthProvider('apple.com');
    try {
        const result = await firebase.auth().createUserWithPopup(provider);
        const idToken = await result.user.getIdToken();
        // Store idToken in local storage or cookie
        document.cookie = `token=${idToken}`;
        window.location.href = '/';
    } catch (error) {
        console.error(error);
    }
}
