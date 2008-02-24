 Dotclear pytrainer extension
 ===============================  
	This extension allows you to post your sport record directly   
	into your dotclear weblog. 
	It work only on a Dotclear 2.0 blog    
	It's a small program to learn python, it's not a revolution but is work


First section in english (for all over the world) 
Second section the same but in french (because dotclear is primary use in France)  

  CONFIG OPTIONS  
  ==============
  	You have to fill in all the fields.    

	xmlrpcserver: to send a new post on your blog, you have to activate the xml/rpc server. when this service is activated dotclear give you a xml/rpc adress ( like http://yourblog.be/index.php/xmlrpc/default )

	bloguser: Your user id for your blog    

	blogpass : Your password that  you use on connect you to your blog
    
	blogid: dotclear 2.0  can accept somes blogs with one  install, you have to define the blog id (by default it's 1 )    

	blogcategory: It's the category's number where this extension post your record on youR blog  

  USAGE  
  =====  
	Simply submit the dotclear extension preferences form and then go  to the record tab and press "post it in dotclear".  
    
  ON YOUR BLOG  
  ============   
 
	I have created a category only for my pytrainer record. I have excluded this category on my homepage and took  a section on the sidebard for show only this category  

	To  exclude the category  
	------------------------  
		You must  (HAVE TO ENCORE ET  TOUJOURS) edit the home.html file on your template directory. And change the <tpl:Entries>  to <tpl:Entries category="!name of your category">  the name of your category is the dotclear name for your categories (without accents and spécial char)      

	To only show the record category on your sidebar  
	-------------------------------------------------


	<tpl:Entries category="training" lastn="4">
		<div class="post">

			<h3 id="p{{tpl:EntryID}}" class="training-title"><a
				href="{{tpl:EntryURL}}">{{tpl:EntryTitle encode_html="1"}}</a></h3>

			<tpl:EntryIf extended="1">
		  	<div class="post-content">{{tpl:EntryExcerpt}}</div>
		  	</tpl:EntryIf>	  
			
			<tpl:EntryIf extended="0">
		  	<div class="training-content">{{tpl:EntryContent}}</div>
			</tpl:EntryIf>
	
		</div>
	</tpl:Entries>

you have to replace training by the category's name      

  THANKS  
  ======    
	Fiz for pytrainer, and is help for every stupid question that i have sent.    
	Gnomefiles for the promotion of somes app's   
	My stupid stage, where if i wanT take something i must have do wath i want

IN FRENCH
  Dotclear pytrainer extension
  ===============================
  Cette extension vous permet d'envoyer vos scores de pytrainer vers votre blog dotclear 2.0


  Options de configuration
  ========================
  Vous devez remplir tous les champs

    xmlrpcserver: pour envoyer un nouveau post sur votre blog, vous devez activer l'interface xml/rpc de votre blog dotclear 2.0. Pour cela rendez-vous sur la page Parametres du blog, il y a une section xml/rpc à activer. Après activation de l'interface, dotclear vous indiquerea une adresse  ( comme http://votre blog.be/index.php/xmlrpc/default )

    bloguser: Votre identifiant de connections a votre blog, votre nom d'utilisateur quoi

    blogpass : Le mot de passe que vous utilisez pour vous connecter a votre blog (n'ayez crainte personne, ne le verra)

    blogid: Dotclear 2.0 peut faire plusieurs blogs différents avec une seule installation (le multiblog que ça s'appelle) pour que cette extension sache où envoyer votre post, il faut lui dire vers quel blog (par défaut c'est 1 )

    blogcategory: Chaque catégorie crée dans votre blog à un nº (par ordre de création, donc général a le nº 1), il s'agit de la catégorie dans laquelle cette extension enverra les données de votre score. Pour trouver le nº de la catégorie vous cliquez sur Catégories dans la colonne de gauche de l'interface d'administration de votre blog, vous cliquez sur la catégorie et dans la barre d'adresse de votre navigateur vous trouverez un truc comme admin/category.php?id=5   et bien ici le nº de la catégorie est 5

  UTILISATION
  ===========
  
  Dans la fenêtre qui donne les détails sur un record, vous devez avoir en bas à droite un petit bouton "Post in Dotclear"   et hop cette extension grâce a l'aide de pytrainer enverra certaines informations de votre score sur votre blog   

 
  SUR VOTRE BLOG
  ============
  
  J'ai créé une catégorie exprès pour mes scores de pytrainer. J'ai exclu cette catégorie de ma page d'accueil et utilisé une partie de ma barre latérale pour montrer uniquement cette catégorie

  Pour exclure la catégorie
  ------------------------
  Vous devez éditer le fichier home.html dans le dossier de votre template. Et remplacer le code <tpl:Entries>  par <tpl:Entries category="!nom de la categorie"> . le nom de la catégorie doit être le nom de votre catégorie selon dotclear (sans accents et sans caractères spéciaux)

  
  
  Pour uniquement montrer la catégorie avec vos record dans la barre latérale
  -------------------------------------------------

	<tpl:Entries category="entrainements" lastn="4">
		<div class="post">

			<h3 id="p{{tpl:EntryID}}" class="entrainements-title"><a
				href="{{tpl:EntryURL}}">{{tpl:EntryTitle encode_html="1"}}</a></h3>

			<tpl:EntryIf extended="1">
		  	<div class="post-content">{{tpl:EntryExcerpt}}</div>
		  	</tpl:EntryIf>	 
		  	<tpl:EntryIf extended="0">
		  	<div class="entrainements-content">{{tpl:EntryContent}}</div>
			</tpl:EntryIf>
	 
				
		</div>
	</tpl:Entries>

il faut remplacer entrainements par le nom de votre catégorie, et 4 dans lastn=""  c'est le nombre de billets affichés
