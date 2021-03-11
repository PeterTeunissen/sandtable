<form method="post" action="draw">
 <input name="action" type="hidden" value="load">
 <div class="historybox">
  <br><span class="historyTitle">Saved</span><br>
  %for n,t,f in zip(save,mtimes(save),ftime(save)):
   <button class="history" type="submit" name="_loadname" value="{{n}}"><img src="{{path}}{{n}}.png?{{t}}" alt="{{n}}"><br>{{n}} {{f}}</button>
  %end
  <br><span class="historyTitle">History</span><br>
  %for n,t,f in zip(history,mtimes(history),ftime(history)):
   <button class="history" type="submit" name="_loadname" value="{{n}}"><img src="{{path}}{{n}}.png?{{t}}" alt="{{n}}"><br>{{n}} {{f}}</button>
  %end
  <br><span class="historyTitle">Jobs</span><br>
  %for n,t,f in zip(jobs,mtimes(jobs),ftime(jobs)):
   <button class="history" type="submit" name="_loadname" value="{{n}}"><img src="{{path}}{{n}}.png?{{t}}" alt="{{n}}"><br>{{n}} {{f}}</button>
  %end
 </div>
</form>

