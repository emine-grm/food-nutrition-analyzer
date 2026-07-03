/* ============================================================
   NOURA — State
   Mirrors the shape produced by core/profile.py, core/tracker.py
   and core/recommender.py so the UI can be wired to the real
   backend later with minimal changes.
   ============================================================ */

const NouraState = (function(){
  const KEY = 'noura_state_v1';

  const defaultState = {
    onboarded:false,
    profile:{
      name:"Amina",
      age:24, weight_kg:58, height_cm:165, gender:"female",
      goal:"lose_weight",
      restrictions:["halal"],
      language:"en",
      daily_targets:{ calories:1850, protein_g:120, carbs_g:180, fat_g:60 }
    },
    today:{
      totals:{ calories:0, protein_g:0, carbs_g:0, fat_g:0 },
      meals:[]
    },
    history:[
      { id:'h1', date:'2026-06-30', name:'Grilled chicken & rice', img:'assets/burger.jpg', calories:520, score:88, verdict:'great', time:'1:05 PM' },
      { id:'h2', date:'2026-06-30', name:'Greek yogurt & berries', img:'assets/burger.jpg', calories:210, score:94, verdict:'great', time:'8:15 AM' },
      { id:'h3', date:'2026-06-29', name:'Beef burger & fries', img:'assets/burger.jpg', calories:820, score:52, verdict:'caution', time:'7:40 PM' },
      { id:'h4', date:'2026-06-29', name:'Vegetable stir fry', img:'assets/burger.jpg', calories:340, score:90, verdict:'great', time:'12:30 PM' },
      { id:'h5', date:'2026-06-28', name:'Falafel wrap', img:'assets/burger.jpg', calories:480, score:76, verdict:'good', time:'1:20 PM' }
    ],
    lastAnalysis:null
  };

  function load(){
    try{
      const raw = localStorage.getItem(KEY);
      if(!raw) return structuredClone(defaultState);
      const parsed = JSON.parse(raw);
      return Object.assign(structuredClone(defaultState), parsed);
    }catch(e){
      return structuredClone(defaultState);
    }
  }
  function save(state){
    try{ localStorage.setItem(KEY, JSON.stringify(state)); }catch(e){}
  }
  function get(){ return load(); }
  function update(fn){
    const s = load();
    fn(s);
    save(s);
    return s;
  }
  function reset(){ save(structuredClone(defaultState)); }

  // ---- Nutrition helper: matches core/recommender.py meal_verdict() ----
  function scoreMeal(nutrition, targets){
    let score = 100;
    const positives = [];
    const concerns = [];

    const calFrac = nutrition.calories / (targets.calories * 0.35 || 1);
    if(nutrition.calories > targets.calories * 0.45){ score -= 15; concerns.push('note_cal_high'); }
    else if(nutrition.calories > targets.calories * 0.25){ concerns.push('note_cal_mid'); }
    else { positives.push('note_cal_low'); }

    if(nutrition.protein_g > 20){ positives.push('note_protein_high'); score += 5; }
    else if(nutrition.protein_g > 10){ positives.push('note_protein_mid'); }
    else { concerns.push('note_protein_low'); score -= 8; }

    if(nutrition.fiber_g > 5){ positives.push('note_fiber_high'); score += 4; }
    else if(nutrition.fiber_g > 2){ positives.push('note_fiber_mid'); }
    else { concerns.push('note_fiber_low'); score -= 4; }

    if(nutrition.sugar_g > 20){ concerns.push('note_sugar_high'); score -= 12; }
    else if(nutrition.sugar_g > 10){ concerns.push('note_sugar_mid'); }
    else { positives.push('note_sugar_low'); }

    if(nutrition.fat_g > 20){ concerns.push('note_fat_high'); score -= 10; }
    else if(nutrition.fat_g > 10){ concerns.push('note_fat_mid'); }
    else { positives.push('note_fat_low'); }

    if(nutrition.sodium_mg > 600){ concerns.push('note_sodium_high'); score -= 10; }
    else if(nutrition.sodium_mg > 300){ concerns.push('note_sodium_mid'); }
    else { positives.push('note_sodium_low'); }

    score = Math.max(5, Math.min(100, Math.round(score)));
    let verdict = 'great';
    if(score < 55) verdict = 'caution';
    else if(score < 78) verdict = 'good';

    return { score, verdict, positives, concerns };
  }

  return { get, update, save, reset, scoreMeal, defaultState };
})();
