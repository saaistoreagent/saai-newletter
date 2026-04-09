/**
 * Google Apps Script — 스토어레터 피드백 (페이지 서빙 + 데이터 수집)
 *
 * 설정: 기존 배포를 "새 버전"으로 업데이트하면 됩니다.
 * 1. Apps Script 편집기에서 이 코드로 교체
 * 2. 배포 → 배포 관리 → 연필 아이콘 → 새 버전 → 배포
 *
 * 사용: 뉴스레터에 아래 링크만 넣으면 끝
 * https://script.google.com/macros/s/AKfycb.../exec?week=4월2주차&keywords=버터떡,두쫀쿠,...
 */

const SHEET_ID = '11A4rzi8JwXGef0YnvzHRC_yC6dBUS7a7aCbG5CTemEI';
const SHEET_NAME = '피드백';

// ── GET: 피드백 페이지 서빙 ──
function doGet(e) {
  const week = (e && e.parameter && e.parameter.week) || '';
  const keywords = (e && e.parameter && e.parameter.keywords) || '버터떡,두쫀쿠,단백질쉐이크,프링글스 초코블럭,박은영 마라샹궈,정호영 다카마쓰우동';
  const sub = (e && e.parameter && e.parameter.sub) || '';

  const html = HtmlService.createHtmlOutput(getPageHtml(week, keywords, sub))
    .setTitle('스토어레터 피드백')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);

  // 모바일 최적화
  html.addMetaTag('viewport', 'width=device-width, initial-scale=1.0, maximum-scale=1.0');

  return html;
}

// ── POST: 피드백 저장 ──
function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);

    const ss = SpreadsheetApp.openById(SHEET_ID);
    let sheet = ss.getSheetByName(SHEET_NAME);

    if (!sheet) {
      sheet = ss.insertSheet(SHEET_NAME);
      sheet.appendRow(['시간', '주차', '구독자', '만족도', '도움된 키워드', '발주/진열 변경', '변경 내용', '자유 의견']);
      sheet.getRange(1, 1, 1, 8).setFontWeight('bold').setBackground('#ebf0fc');
      sheet.setFrozenRows(1);
    }

    sheet.appendRow([
      data.timestamp || new Date().toISOString(),
      data.week || '',
      data.subscriber || '',
      data.satisfaction || '',
      (data.helpfulKeywords || []).join(', '),
      data.tookAction || '',
      data.actionDetail || '',
      data.freeText || ''
    ]);

    return ContentService
      .createTextOutput(JSON.stringify({ status: 'ok' }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ status: 'error', message: err.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

// ── 피드백 페이지 HTML ──
function getPageHtml(week, keywords, sub) {
  const kwArray = keywords.split(',').map(k => k.trim());
  const chipHtml = kwArray.map(k => `<div class="chip" onclick="this.classList.toggle('selected')">${k}</div>`).join('');

  return `<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Pretendard',-apple-system,BlinkMacSystemFont,sans-serif;background:#24282d;color:#3d434d;line-height:1.7;-webkit-font-smoothing:antialiased}
.wrap{max-width:480px;margin:0 auto;padding:24px 16px}
.card{background:#fff;border:1px solid #e9e9ea;border-radius:12px;padding:28px 24px;margin-bottom:12px}
.card.hidden{display:none}
.card.fade-in{animation:fadeIn .3s ease}
@keyframes fadeIn{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
.header{background:#376ae2;border-radius:12px;padding:24px;margin-bottom:16px;text-align:center}
.header-logo{font-size:13px;font-weight:700;color:rgba(255,255,255,.5);letter-spacing:.12em;margin-bottom:12px}
.header-title{font-size:22px;font-weight:700;color:#fff;line-height:1.4}
.header-sub{font-size:13px;color:rgba(255,255,255,.6);margin-top:6px}
.step-label{font-size:11px;font-weight:600;color:#376ae2;background:#ebf0fc;display:inline-block;padding:2px 10px;border-radius:999px;margin-bottom:12px;letter-spacing:.04em}
.question{font-size:17px;font-weight:600;color:#24282d;margin-bottom:16px;line-height:1.5}
.hint{font-size:12px;color:#8e949d;margin-bottom:12px}
.emoji-row{display:flex;gap:12px;justify-content:center}
.emoji-btn{width:72px;height:72px;border:2px solid #e9e9ea;border-radius:16px;background:#f9f9fb;font-size:32px;cursor:pointer;transition:all .15s;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:4px}
.emoji-btn:active{transform:scale(.95)}
.emoji-btn.selected{border-color:#376ae2;background:#ebf0fc;box-shadow:0 0 0 3px rgba(55,106,226,.15)}
.emoji-label{font-size:10px;color:#565f6c;font-weight:500}
.chip-grid{display:flex;flex-wrap:wrap;gap:8px}
.chip{padding:8px 16px;border:1.5px solid #e9e9ea;border-radius:999px;background:#fff;font-size:14px;font-weight:500;color:#3d434d;cursor:pointer;transition:all .15s;user-select:none}
.chip:active{transform:scale(.96)}
.chip.selected{border-color:#376ae2;background:#ebf0fc;color:#376ae2}
.option-row{display:flex;gap:8px}
.option-btn{flex:1;padding:14px;border:1.5px solid #e9e9ea;border-radius:10px;background:#fff;font-size:14px;font-weight:600;color:#3d434d;cursor:pointer;text-align:center;transition:all .15s}
.option-btn:active{transform:scale(.97)}
.option-btn.selected{border-color:#376ae2;background:#ebf0fc;color:#376ae2}
.text-input{width:100%;padding:12px 16px;border:1.5px solid #e9e9ea;border-radius:10px;font-family:inherit;font-size:14px;color:#3d434d;resize:none;outline:none;transition:border-color .15s}
.text-input:focus{border-color:#376ae2}
.text-input::placeholder{color:#8e949d}
.inline-input{margin-top:10px}
.inline-input.hidden{display:none}
.submit-btn{width:100%;padding:16px;background:#376ae2;color:#fff;border:none;border-radius:10px;font-family:inherit;font-size:15px;font-weight:700;cursor:pointer;transition:all .15s}
.submit-btn:active{transform:scale(.98)}
.submit-btn:disabled{background:#e9e9ea;color:#8e949d;cursor:not-allowed}
.skip-link{display:block;text-align:center;margin-top:10px;font-size:13px;color:#8e949d;cursor:pointer}
.done-card{text-align:center;padding:48px 24px}
.done-emoji{font-size:48px;margin-bottom:16px}
.done-title{font-size:20px;font-weight:700;color:#24282d;margin-bottom:8px}
.done-sub{font-size:14px;color:#565f6c}
.progress{height:3px;background:#e9e9ea;border-radius:2px;margin-bottom:16px;overflow:hidden}
.progress-bar{height:100%;background:#376ae2;border-radius:2px;transition:width .4s ease}
</style>
</head>
<body>
<div class="wrap">
  <div class="header">
    <div class="header-logo">STORE LETTER</div>
    <div class="header-title">30초 피드백</div>
    <div class="header-sub">${week ? week + ' 스토어레터는 어땠나요?' : '이번 주 스토어레터는 어땠나요?'}</div>
  </div>
  <div class="progress"><div class="progress-bar" id="pb" style="width:0%"></div></div>

  <div class="card fade-in" id="s1">
    <div class="step-label">1 / 4</div>
    <div class="question">발주에 도움이 됐나요?</div>
    <div class="emoji-row">
      <div class="emoji-btn" data-v="good" onclick="emo(this)"><span>😍</span><span class="emoji-label">많이 됐어요</span></div>
      <div class="emoji-btn" data-v="okay" onclick="emo(this)"><span>😊</span><span class="emoji-label">조금 됐어요</span></div>
      <div class="emoji-btn" data-v="meh" onclick="emo(this)"><span>😐</span><span class="emoji-label">모르겠어요</span></div>
    </div>
  </div>

  <div class="card hidden" id="s2">
    <div class="step-label">2 / 4</div>
    <div class="question">가장 도움된 키워드는요?</div>
    <div class="hint">여러 개 선택할 수 있어요</div>
    <div class="chip-grid" id="cg">${chipHtml}</div>
    <div class="skip-link" onclick="go(3)">딱히 없어요 →</div>
  </div>

  <div class="card hidden" id="s3">
    <div class="step-label">3 / 4</div>
    <div class="question">실제로 발주하거나 진열을 바꾼 게 있나요?</div>
    <div class="option-row">
      <div class="option-btn" data-v="yes" onclick="act(this)">있어요</div>
      <div class="option-btn" data-v="no" onclick="act(this)">아직 없어요</div>
    </div>
    <div class="inline-input hidden" id="ad"><textarea class="text-input" id="at" rows="2" placeholder="뭘 바꿨는지 짧게 알려주세요 (선택)"></textarea></div>
  </div>

  <div class="card hidden" id="s4">
    <div class="step-label">4 / 4</div>
    <div class="question">바라는 점이 있다면 자유롭게 적어주세요</div>
    <div class="hint">안 적어도 괜찮아요</div>
    <textarea class="text-input" id="ft" rows="3" placeholder="예: 음료 트렌드를 더 다뤄줬으면 좋겠어요"></textarea>
  </div>

  <div class="card hidden" id="sc"><button class="submit-btn" id="sb" onclick="send()">피드백 보내기</button></div>

  <div class="card hidden" id="dc">
    <div class="done-card">
      <div class="done-emoji">🎉</div>
      <div class="done-title">감사합니다!</div>
      <div class="done-sub">다음 주 스토어레터에 반영할게요</div>
    </div>
  </div>
</div>

<script>
var D={week:'${week}',subscriber:'${sub}',satisfaction:'',helpfulKeywords:[],tookAction:'',actionDetail:'',freeText:'',timestamp:''};
var step=1;
function pb(){document.getElementById('pb').style.width=Math.min((step-1)/4*100,100)+'%'}
function show(n){var c=document.getElementById('s'+n);if(c){c.classList.remove('hidden');c.classList.add('fade-in');c.scrollIntoView({behavior:'smooth',block:'center'})}}
function go(n){step=n;pb();show(n);if(n>=4){setTimeout(function(){var s=document.getElementById('sc');s.classList.remove('hidden');s.classList.add('fade-in')},200)}}
function emo(el){document.querySelectorAll('.emoji-btn').forEach(function(b){b.classList.remove('selected')});el.classList.add('selected');D.satisfaction=el.getAttribute('data-v');setTimeout(function(){go(2)},300)}
var ct=null;document.getElementById('cg').addEventListener('click',function(){clearTimeout(ct);ct=setTimeout(function(){go(3)},1500)});
function act(el){document.querySelectorAll('.option-btn').forEach(function(b){b.classList.remove('selected')});el.classList.add('selected');D.tookAction=el.getAttribute('data-v');var d=document.getElementById('ad');if(el.getAttribute('data-v')==='yes'){d.classList.remove('hidden')}else{d.classList.add('hidden')}setTimeout(function(){go(4)},500)}
function send(){var b=document.getElementById('sb');b.disabled=true;b.textContent='보내는 중...';D.helpfulKeywords=[];document.querySelectorAll('.chip.selected').forEach(function(c){D.helpfulKeywords.push(c.textContent)});D.actionDetail=document.getElementById('at').value;D.freeText=document.getElementById('ft').value;D.timestamp=new Date().toISOString();
var url=window.location.href.split('?')[0];
fetch(url,{method:'POST',mode:'no-cors',headers:{'Content-Type':'application/json'},body:JSON.stringify(D)}).then(function(){done()}).catch(function(){done()});
function done(){document.getElementById('sc').classList.add('hidden');document.getElementById('s4').classList.add('hidden');var dc=document.getElementById('dc');dc.classList.remove('hidden');dc.classList.add('fade-in');dc.scrollIntoView({behavior:'smooth',block:'center'});document.getElementById('pb').style.width='100%'}}
}
</script>
</body></html>`;
}
