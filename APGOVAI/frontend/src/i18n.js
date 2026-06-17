export const LANGUAGES = [
  {
    code: "en",
    label: "English",
  },
  {
    code: "te",
    label: "తెలుగు",
  },
];

export const DEFAULT_LANGUAGE = "en";

const TEXT = {
  en: {
    common: {
      language: "Language",
      english: "English",
      telugu: "Telugu",
      back: "Back",
      delete: "Delete",
      upload: "Upload",
      status: "Status",
      action: "Action",
      file: "File",
      collection: "Collection",
    },
    app: {
      subtitle: "AI Assistant for Andhra Pradesh Government",
      title: "How can I help you today?",
      description:
        "Ask APGovAI about Government Orders, Budgets, Policies, Circulars, Reports and Acts.",
      placeholder: "Ask APGovAI...",
      thinking: "Generating response...",
    },
    leaders: {
      chiefMinister: "Chief Minister",
      deputyChiefMinister: "Deputy CM",
      itMinister: "IT Minister",
    },
    sidebar: {
      newConversation: "New Conversation",
      navigation: "Navigation",
      chats: "Chats",
      users: "Users",
      documents: "Documents",
      recentConversations: "Recent Conversations",
      logout: "Logout",
      deleteConversation: "Delete conversation",
    },
    chat: {
      send: "Send",
    },
    login: {
      signIn: "Sign In",
      username: "Username",
      password: "Password",
      login: "Login",
      invalidCredentials: "Invalid credentials",
    },
    users: {
      title: "User Management",
      createUser: "Create User",
      username: "Username",
      password: "Password",
      role: "Role",
      status: "Status",
      active: "Active",
      disabled: "Disabled",
      user: "User",
      admin: "Admin",
    },
    documents: {
      title: "Document Management",
      governmentOrders: "Government Orders",
      budgets: "Budgets",
      reports: "Reports",
      datasets: "Datasets",
      file: "File",
      collection: "Collection",
      status: "Status",
      action: "Action",
      completed: "Completed",
      processing: "Processing",
      failed: "Failed",
    },
  },
  te: {
    common: {
      language: "భాష",
      english: "ఇంగ్లీష్",
      telugu: "తెలుగు",
      back: "వెనుకకు",
      delete: "తొలగించు",
      upload: "అప్‌లోడ్",
      status: "స్థితి",
      action: "చర్య",
      file: "ఫైల్",
      collection: "వర్గం",
    },
    app: {
      subtitle: "ఆంధ్రప్రదేశ్ ప్రభుత్వానికి AI సహాయకుడు",
      title: "ఈ రోజు నేను మీకు ఎలా సహాయం చేయగలను?",
      description:
        "ప్రభుత్వ ఉత్తర్వులు, బడ్జెట్లు, విధానాలు, సర్క్యులర్లు, నివేదికలు, మరియు చట్టాల గురించి APGovAIను అడగండి.",
      placeholder: "APGovAIను అడగండి...",
      thinking: "సమాధానం సిద్ధమవుతోంది...",
    },
    leaders: {
      chiefMinister: "ముఖ్యమంత్రి",
      deputyChiefMinister: "ఉప ముఖ్యమంత్రి",
      itMinister: "ఐటీ మంత్రి",
    },
    sidebar: {
      newConversation: "కొత్త సంభాషణ",
      navigation: "నావిగేషన్",
      chats: "సంభాషణలు",
      users: "వినియోగదారులు",
      documents: "పత్రాలు",
      recentConversations: "ఇటీవలి సంభాషణలు",
      logout: "లాగ్ అవుట్",
      deleteConversation: "సంభాషణను తొలగించు",
    },
    chat: {
      send: "పంపు",
    },
    login: {
      signIn: "సైన్ ఇన్",
      username: "వినియోగదారు పేరు",
      password: "పాస్‌వర్డ్",
      login: "లాగిన్",
      invalidCredentials: "చెల్లని వివరాలు",
    },
    users: {
      title: "వినియోగదారుల నిర్వహణ",
      createUser: "వినియోగదారుడిని సృష్టించండి",
      username: "వినియోగదారు పేరు",
      password: "పాస్‌వర్డ్",
      role: "పాత్ర",
      status: "స్థితి",
      active: "క్రియాశీలం",
      disabled: "నిష్క్రియం",
      user: "వినియోగదారు",
      admin: "నిర్వాహకుడు",
    },
    documents: {
      title: "పత్రాల నిర్వహణ",
      governmentOrders: "ప్రభుత్వ ఉత్తర్వులు",
      budgets: "బడ్జెట్లు",
      reports: "నివేదికలు",
      datasets: "డేటాసెట్లు",
      file: "ఫైల్",
      collection: "వర్గం",
      status: "స్థితి",
      action: "చర్య",
      completed: "పూర్తయింది",
      processing: "ప్రాసెస్ అవుతోంది",
      failed: "విఫలమైంది",
    },
  },
};

export function getInitialLanguage() {
  const stored = localStorage.getItem("language");
  return TEXT[stored] ? stored : DEFAULT_LANGUAGE;
}

export function getText(language) {
  return TEXT[language] || TEXT[DEFAULT_LANGUAGE];
}

export function getRoleLabel(role, t) {
  if (role === "admin") {
    return t.users.admin;
  }

  return t.users.user;
}
