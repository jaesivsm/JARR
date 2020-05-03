const prefix = "jarr-";

function getStorage(storage) {
  if (!storage || storage === "local") {
      return localStorage;
  } else {
      return sessionStorage;
  }
}

export function storageGet(key, storage) {
  return getStorage(storage).getItem(prefix + key);
}

export function storageSet(key, value, storage) {
  return getStorage(storage).setItem(prefix + key, value);
}

export function storageRemove(key, storage) {
  return getStorage(storage).removeItem(prefix + key);
}
