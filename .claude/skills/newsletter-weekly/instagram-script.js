// 인스타그램 피드 긁기 스크립트
// 사용법: IG 웹사이트 로그인 → DevTools(Cmd+Option+I) → Console 탭 →
//         "allow pasting" 입력 후 엔터 → 아래 전체 붙여넣기 → 엔터

(async () => {
  const posts = new Map();
  console.log('🔄 스크롤 시작 (약 50초 소요)...');
  for (let i = 0; i < 25; i++) {
    window.scrollTo(0, document.body.scrollHeight);
    await new Promise(r => setTimeout(r, 2000));
    document.querySelectorAll('article').forEach(a => {
      const l = a.querySelector('a[href*="/p/"],a[href*="/reel/"]');
      if (l && !posts.has(l.href)) posts.set(l.href, a.innerText);
    });
    console.log(`[${i+1}/25] 수집 ${posts.size}개`);
  }
  const text = Array.from(posts.entries())
    .map(([u, c]) => `--- ${u} ---\n${c}`).join('\n\n');
  window._igFeed = text;
  try {
    await navigator.clipboard.writeText(text);
    console.log(`✅ ${posts.size}개 포스트 클립보드 복사 완료. Claude 채팅에 Cmd+V`);
  } catch (e) {
    console.log(`⚠️ 자동 복사 실패. 아래 명령 입력: copy(window._igFeed)`);
  }
})();
